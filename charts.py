import io
import math
import typing as t

import cairo
import numpy as np

from models.employee_options import EmployeeOptions

def save_roi_distribution_chart(function_name: str, roi_list: t.List[float], employee_options: EmployeeOptions, save: bool = False, top_value: t.Optional[t.SupportsFloat] = None) -> bytes:
    # Set up the surface and context
    width, height = 800, 600
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    # Set white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    minim=0
    # 11 bins, with the 2nd bin being the discount rate
    # Adjusted to this random formula
    if top_value is None:
        maxim=round(
            np.mean(roi_list) + (np.std(roi_list) * 3)
            , 2
        )   
    else:
        maxim=top_value
    
    # Calculate histogram data
    for i in range(len(roi_list)):
        if roi_list[i] < 0:
            roi_list[i] = 0
        elif roi_list[i] > maxim:
            roi_list[i] = maxim-0.01
    bins = 11 # int((maxim - minim) / 0.05)

    hist, bin_edges = np.histogram(roi_list, bins=bins, range=(minim, maxim))
    
    # Set up the plot area
    margin = 70
    plot_width = width - 2 * margin
    plot_height = height - 2 * margin
    
    # Draw axes
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(2)
    ctx.move_to(margin, height - margin)
    ctx.line_to(width - margin, height - margin)  # x-axis
    ctx.move_to(margin, height - margin)
    ctx.line_to(margin, margin)  # y-axis
    ctx.stroke()
    
    # Draw histogram bars
    bar_width = plot_width / bins
    max_count = max(500, max(hist))
    
    for i, count in enumerate(hist):
        # Calculate bar height
        bar_height = (count / max_count) * plot_height
        
        # Set blue color with transparency
        ctx.set_source_rgba(0, 0, 1, 0.7)
        
        # Draw bar
        x = margin + i * bar_width
        y = height - margin - bar_height
        ctx.rectangle(x, y, bar_width - 1, bar_height)
        ctx.fill()
        
        # Draw count text
        if count > 0:
            ctx.set_source_rgb(0, 0, 0)
            ctx.set_font_size(24)
            text = str(int(count))
            text_extents = ctx.text_extents(text)
            ctx.move_to(x + bar_width/2 - text_extents.width/2, y - 5)
            ctx.show_text(text)
    
    # Draw title and labels
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(24)
    
    # Title
    title = f"ROI Distribution"
    text_extents = ctx.text_extents(title)
    ctx.move_to(width/2 - text_extents.width/2, margin/2)
    ctx.show_text(title)
    
    # X-axis label
    x_label = "ROI"
    arbitrary_offset = 50
    text_extents = ctx.text_extents(x_label)
    ctx.move_to(width/2 - text_extents.width/2 - arbitrary_offset, height - margin/2)
    ctx.show_text(x_label)
    
    # Y-axis label
    y_label = f"Frequency in {len(roi_list)} runs"
    ctx.save()
    ctx.translate(margin/2 - 10, height/2)  # Add more padding by subtracting 20 from margin/2
    ctx.rotate(-math.pi/2)
    text_extents = ctx.text_extents(y_label)
    ctx.move_to(-text_extents.width/2, 0)
    ctx.show_text(y_label)
    ctx.restore()
    # Draw grid lines
    ctx.set_source_rgba(0, 0, 0, 0.2)
    ctx.set_line_width(1)
    
    # Vertical grid lines with ROI labels
    for i in range(bins + 1):  # 10 points to create 11 intervals
        x = margin + (i * plot_width / bins)
        
        # Set color for grid lines
        ctx.set_source_rgba(0, 0, 0, 1)  # Ensure grid lines are light gray
        # Draw grid line
        ctx.move_to(x, margin)
        ctx.line_to(x, height - margin)
        ctx.stroke()
        
        roi_value = minim + (i * maxim / bins)  # Map from -0.1 to 1.0
        # Add ROI label
        if i % 2 == 0 and roi_value not in [0.0]:
            
            label = f"{int(float(roi_value) * 100)}%"
            if i == bins - 1:
                label = f">{label}"
            text_extents = ctx.text_extents(label)
            ctx.set_source_rgb(0, 0, 0)
            ctx.set_font_size(16)  # Smaller font size to fit more labels
            ctx.move_to(x - text_extents.width/2, height - margin + 15)
            ctx.show_text(label)
    
    # Horizontal grid lines
    for i in range(5):
        y = height - margin - (i * plot_height / 4)
        ctx.move_to(margin, y)
        ctx.line_to(width - margin, y)
        ctx.stroke()
        
        # Add frequency label
        freq = int(max_count * (i / 4))
        label = str(freq)
        text_extents = ctx.text_extents(label)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_font_size(16)
        ctx.move_to(margin - text_extents.width - 5, y + text_extents.height/2)
        ctx.show_text(label)
    
    # Save the surface to a file
    if save:
        surface.write_to_png(f'{function_name}_roi_distribution.png')
    
    # Get the PNG data as bytes
    png_data = io.BytesIO()
    surface.write_to_png(png_data)
    png_bytes = png_data.getvalue()
    
    # Clean up
    surface.finish()
    png_data.close()
    
    return png_bytes
