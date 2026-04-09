"""
Bill Generation utility for electricity bills
"""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO


# Karnataka Electricity Provider Tariffs (as of 2025)
PROVIDER_TARIFFS = {
    'MESCOM': {
        'name': 'Mangalore Electricity Supply Company Ltd.',
        'fixed_charge': 100,
        'slabs': [
            {'up_to': 50, 'rate': 3.40},
            {'up_to': 100, 'rate': 4.95},
            {'up_to': 200, 'rate': 6.50},
            {'above': 200, 'rate': 7.55}
        ]
    },
    'BESCOM': {
        'name': 'Bangalore Electricity Supply Company Ltd.',
        'fixed_charge': 120,
        'slabs': [
            {'up_to': 50, 'rate': 3.75},
            {'up_to': 100, 'rate': 5.20},
            {'up_to': 200, 'rate': 6.75},
            {'above': 200, 'rate': 7.80}
        ]
    },
    'HESCOM': {
        'name': 'Hubli Electricity Supply Company Ltd.',
        'fixed_charge': 90,
        'slabs': [
            {'up_to': 50, 'rate': 3.50},
            {'up_to': 100, 'rate': 5.00},
            {'up_to': 200, 'rate': 6.60},
            {'above': 200, 'rate': 7.60}
        ]
    },
    'GESCOM': {
        'name': 'Gulbarga Electricity Supply Company Ltd.',
        'fixed_charge': 85,
        'slabs': [
            {'up_to': 50, 'rate': 3.45},
            {'up_to': 100, 'rate': 4.90},
            {'up_to': 200, 'rate': 6.55},
            {'above': 200, 'rate': 7.50}
        ]
    },
    'CESC': {
        'name': 'Chamundeshwari Electricity Supply Corporation Ltd.',
        'fixed_charge': 95,
        'slabs': [
            {'up_to': 50, 'rate': 3.60},
            {'up_to': 100, 'rate': 5.10},
            {'up_to': 200, 'rate': 6.70},
            {'above': 200, 'rate': 7.70}
        ]
    },
    'OTHER': {
        'name': 'Other Provider',
        'fixed_charge': 100,
        'slabs': [
            {'up_to': 50, 'rate': 3.50},
            {'up_to': 100, 'rate': 5.00},
            {'up_to': 200, 'rate': 6.50},
            {'above': 200, 'rate': 7.50}
        ]
    }
}


def validate_rr_number(rr_number, provider):
    """
    Validate RR/MR number format (dummy validation)
    In production, this would call actual provider API
    """
    if not rr_number:
        return False, "RR number is required"
    
    # Basic format validation
    if len(rr_number) < 8:
        return False, "RR number must be at least 8 characters"
    
    # Provider-specific validation (dummy)
    if provider in ['MESCOM', 'BESCOM', 'HESCOM', 'GESCOM', 'CESC']:
        if not rr_number.startswith('RR') and not rr_number.startswith('MR'):
            return False, f"RR number for {provider} should start with RR or MR"
    
    return True, "Valid RR number"


def get_provider_tariff(provider):
    """Get tariff structure for electricity provider"""
    return PROVIDER_TARIFFS.get(provider, PROVIDER_TARIFFS['OTHER'])


def calculate_bill(units_consumed, provider):
    """
    Calculate electricity bill based on provider tariff
    Returns: dict with bill breakdown
    """
    tariff = get_provider_tariff(provider)
    
    fixed_charge = tariff['fixed_charge']
    slabs = tariff['slabs']
    
    # Calculate energy charges by slab
    remaining_units = units_consumed
    energy_charge = 0
    slab_breakdown = []
    
    for slab in slabs:
        if remaining_units <= 0:
            break
        
        if 'up_to' in slab:
            # Calculate for this slab
            slab_limit = slab['up_to']
            prev_limit = slab_breakdown[-1]['up_to'] if slab_breakdown else 0
            slab_units = min(remaining_units, slab_limit - prev_limit)
            
            if slab_units > 0:
                slab_charge = slab_units * slab['rate']
                energy_charge += slab_charge
                
                slab_breakdown.append({
                    'from': round(prev_limit, 2),
                    'up_to': round(prev_limit + slab_units, 2),
                    'units': round(slab_units, 2),
                    'rate': round(slab['rate'], 2),
                    'charge': round(slab_charge, 2)
                })
                
                remaining_units -= slab_units
        else:
            # Above slab (remaining units)
            if remaining_units > 0:
                slab_charge = remaining_units * slab['rate']
                energy_charge += slab_charge
                
                prev_limit = slab_breakdown[-1]['up_to'] if slab_breakdown else 0
                slab_breakdown.append({
                    'from': round(prev_limit, 2),
                    'up_to': round(prev_limit + remaining_units, 2),
                    'units': round(remaining_units, 2),
                    'rate': round(slab['rate'], 2),
                    'charge': round(slab_charge, 2)
                })
                
                remaining_units = 0
    
    # Calculate total
    subtotal = energy_charge + fixed_charge
    
    # Add taxes (5% as example)
    tax_rate = 0.05
    tax_amount = subtotal * tax_rate
    
    total_amount = subtotal + tax_amount
    
    return {
        'provider': tariff['name'],
        'units_consumed': round(units_consumed, 2),
        'fixed_charge': round(fixed_charge, 2),
        'energy_charge': round(energy_charge, 2),
        'slab_breakdown': slab_breakdown,
        'subtotal': round(subtotal, 2),
        'tax_rate': round(tax_rate * 100, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2)
    }


def generate_bill_pdf(user, billing_period, units_consumed):
    """
    Generate electricity bill PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=30, leftMargin=30,
                          topMargin=30, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Get provider and calculate bill
    provider = user.electricity_provider or 'OTHER'
    bill_data = calculate_bill(units_consumed, provider)
    
    # Title
    title = Paragraph(f"<b>{bill_data['provider']}</b>", title_style)
    elements.append(title)
    
    subtitle = Paragraph("ELECTRICITY BILL", styles['Heading2'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Consumer Details
    consumer_data = [
        ['Consumer Name:', user.name],
        ['RR Number:', user.rr_number or 'N/A'],
        ['Email:', user.email],
        ['Phone:', user.phone_number or 'N/A'],
        ['Billing Period:', billing_period],
        ['Bill Date:', datetime.now().strftime('%d-%b-%Y')],
    ]
    
    consumer_table = Table(consumer_data, colWidths=[2*inch, 4*inch])
    consumer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(consumer_table)
    elements.append(Spacer(1, 20))
    
    # Consumption Details
    elements.append(Paragraph("<b>Consumption Details</b>", styles['Heading3']))
    elements.append(Spacer(1, 10))
    
    consumption_data = [
        ['Units Consumed', f"{units_consumed:.2f} kWh"],
        ['Fixed Charge', f"Rs.{bill_data['fixed_charge']:.2f}"],
    ]
    
    consumption_table = Table(consumption_data, colWidths=[3*inch, 3*inch])
    consumption_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(consumption_table)
    elements.append(Spacer(1, 20))
    
    # Slab-wise Breakdown
    elements.append(Paragraph("<b>Energy Charge Breakdown</b>", styles['Heading3']))
    elements.append(Spacer(1, 10))
    
    slab_data = [['Slab', 'Units', 'Rate (Rs./kWh)', 'Charge (Rs.)']]
    
    for slab in bill_data['slab_breakdown']:
        slab_data.append([
            f"{slab['from']:.0f} - {slab['up_to']:.0f} kWh",
            f"{slab['units']:.2f}",
            f"Rs.{slab['rate']:.2f}",
            f"Rs.{slab['charge']:.2f}"
        ])
    
    slab_table = Table(slab_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    slab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    elements.append(slab_table)
    elements.append(Spacer(1, 20))
    
    # Bill Summary
    elements.append(Paragraph("<b>Bill Summary</b>", styles['Heading3']))
    elements.append(Spacer(1, 10))
    
    summary_data = [
        ['Energy Charge', f"Rs.{bill_data['energy_charge']:.2f}"],
        ['Fixed Charge', f"Rs.{bill_data['fixed_charge']:.2f}"],
        ['Subtotal', f"Rs.{bill_data['subtotal']:.2f}"],
        [f'Tax ({bill_data["tax_rate"]:.0f}%)', f"Rs.{bill_data['tax_amount']:.2f}"],
        ['', ''],
        ['Total Amount Payable', f"Rs.{bill_data['total_amount']:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1a73e8')),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#1a73e8')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = Paragraph(
        "<i>This is a system-generated bill from EnergyTrack. "
        "Tariff rates are based on current provider slabs and may vary.</i>",
        styles['Normal']
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    return buffer
