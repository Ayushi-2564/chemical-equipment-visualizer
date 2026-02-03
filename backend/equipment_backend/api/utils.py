from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from datetime import datetime
import os
from django.conf import settings
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io


def generate_pdf_report(dataset):
    """
    Generate a PDF report for the given dataset
    Returns the path to the generated PDF file
    """
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename
    filename = f"report_{dataset.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
    )
    
    # Title
    title = Paragraph("Chemical Equipment Analysis Report", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Dataset Info
    info_data = [
        ['Dataset Information', ''],
        ['Filename:', dataset.filename],
        ['Upload Date:', dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S')],
        ['Total Equipment:', str(dataset.total_count)],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Summary Statistics
    story.append(Paragraph("Summary Statistics", heading_style))
    
    stats_data = [
        ['Parameter', 'Average Value', 'Unit'],
        ['Flowrate', f'{dataset.avg_flowrate:.2f}', 'm³/h'],
        ['Pressure', f'{dataset.avg_pressure:.2f}', 'bar'],
        ['Temperature', f'{dataset.avg_temperature:.2f}', '°C'],
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Equipment Type Distribution
    story.append(Paragraph("Equipment Type Distribution", heading_style))
    
    type_dist = dataset.get_type_distribution()
    type_data = [['Equipment Type', 'Count', 'Percentage']]
    
    for eq_type, count in type_dist.items():
        percentage = (count / dataset.total_count) * 100
        type_data.append([eq_type, str(count), f'{percentage:.1f}%'])
    
    type_table = Table(type_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(type_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Generate charts
    chart_path = generate_charts(dataset)
    if chart_path:
        story.append(Paragraph("Data Visualization", heading_style))
        story.append(Spacer(1, 0.1*inch))
        img = RLImage(chart_path, width=6*inch, height=4*inch)
        story.append(img)
    
    # Equipment Details Table
    story.append(PageBreak())
    story.append(Paragraph("Equipment Details", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
    
    for equipment in dataset.equipment.all()[:20]:  # Limit to first 20
        equipment_data.append([
            equipment.equipment_name[:20],  # Truncate long names
            equipment.equipment_type[:15],
            f'{equipment.flowrate:.1f}',
            f'{equipment.pressure:.1f}',
            f'{equipment.temperature:.1f}'
        ])
    
    if dataset.equipment.count() > 20:
        equipment_data.append(['...', '...', '...', '...', '...'])
    
    equip_table = Table(equipment_data, colWidths=[1.8*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    equip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(equip_table)
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer = Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Chemical Equipment Visualizer",
        styles['Normal']
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    return filepath


def generate_charts(dataset):
    """Generate matplotlib charts for the dataset"""
    try:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Equipment Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Get data
        type_dist = dataset.get_type_distribution()
        equipment = dataset.equipment.all()
        
        # Chart 1: Equipment Type Distribution (Pie)
        axes[0, 0].pie(
            type_dist.values(), 
            labels=type_dist.keys(), 
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors
        )
        axes[0, 0].set_title('Equipment Type Distribution')
        
        # Chart 2: Average Parameters (Bar)
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [dataset.avg_flowrate, dataset.avg_pressure, dataset.avg_temperature]
        colors_bar = ['#3498db', '#e74c3c', '#2ecc71']
        axes[0, 1].bar(params, values, color=colors_bar)
        axes[0, 1].set_title('Average Parameters')
        axes[0, 1].set_ylabel('Value')
        
        # Chart 3: Equipment Type Count (Bar)
        types = list(type_dist.keys())
        counts = list(type_dist.values())
        axes[1, 0].barh(types, counts, color='#9b59b6')
        axes[1, 0].set_xlabel('Count')
        axes[1, 0].set_title('Equipment Count by Type')
        
        # Chart 4: Parameter Comparison (if enough data)
        if len(equipment) > 0:
            flowrates = [e.flowrate for e in equipment[:10]]
            pressures = [e.pressure for e in equipment[:10]]
            temperatures = [e.temperature for e in equipment[:10]]
            x = range(len(flowrates))
            
            axes[1, 1].plot(x, flowrates, marker='o', label='Flowrate', color='#3498db')
            axes[1, 1].plot(x, pressures, marker='s', label='Pressure', color='#e74c3c')
            axes[1, 1].plot(x, temperatures, marker='^', label='Temperature', color='#2ecc71')
            axes[1, 1].set_title('Parameter Trends (First 10 Equipment)')
            axes[1, 1].set_xlabel('Equipment Index')
            axes[1, 1].set_ylabel('Value')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        chart_filename = f'chart_{dataset.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        chart_path = os.path.join(charts_dir, chart_filename)
        
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"Error generating charts: {e}")
        return None


def process_csv_file(csv_file):
    """
    Process uploaded CSV file and return statistics
    This is a utility function for CSV processing
    """
    import pandas as pd
    
    df = pd.read_csv(csv_file)
    
    # Validate columns
    required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")
    
    # Calculate statistics
    stats = {
        'total_count': len(df),
        'avg_flowrate': float(df['Flowrate'].mean()),
        'avg_pressure': float(df['Pressure'].mean()),
        'avg_temperature': float(df['Temperature'].mean()),
        'type_distribution': df['Type'].value_counts().to_dict(),
        'data': df.to_dict('records')
    }
    
    return stats