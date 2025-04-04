from datetime import datetime
import typing as t
import io

import numpy as np
import cairo
import math

from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters
from espp_scenario_run import ESPPScenarioRun
from models.employee_options import (
    EmployeeOptions
)

from models.espp_result import ESPPResult
import strategies


def run_strategies_against_scenarios(
    prices: np.ndarray,
    employee_options: EmployeeOptions,
    functions: t.Optional[t.List[t.Dict[str, t.Any]]] = None
):
    if functions is None:
        functions = strategies.get_all_strategies()
    for func in functions:
        function_name: str = func["name"] # type: ignore
        print(f'\nRunning scenario {function_name}\n')
        running_ESPPResult = ESPPResult()
        for price in prices:
            espp_state = ESPPScenarioRun(
                price,
                employee_options,
                func["strategy"] # type: ignore
            ).run()
            running_ESPPResult.add(espp_state)

        func['pic_bytes'] = save_roi_distribution_chart(
            function_name,
            running_ESPPResult.roi,
            employee_options
        )
        func['espp_result'] = running_ESPPResult
    return functions

def run_scenarios_against_strategies(
    prices: np.ndarray,
    employee_options: EmployeeOptions,
    functions: t.Optional[t.List[t.Dict[str, t.Any]]] = None
):
    functions = strategies.get_all_strategies()
    for func in functions:
        func["espp_result"] = ESPPResult() 
    for price in prices:
        for func in functions:
            espp_state = ESPPScenarioRun(
                price,
                employee_options,
                func["strategy"]
            ).run()
            func["espp_result"].add(espp_state)
    
    high_mean = 0
    high_std = 0
    for func in functions:
        if np.mean(func["espp_result"].roi) > high_mean:
            high_mean = np.mean(func["espp_result"].roi)
            high_std = np.std(func["espp_result"].roi)

    for func in functions:
        func['pic_bytes'] = save_roi_distribution_chart(func["name"], func["espp_result"].roi, employee_options, top_value=round(high_mean + (high_std * 3), 2))
    return functions

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

def generate_scenarios(
    company_stock_plan: CompanyStockPlan,
    company_stock_start_parameters: CompanyStockStartParameters,
    file_name: t.Optional[str] = None,
    simulations=1000
):
    time_frame = 1
    steps = int(company_stock_plan.pay_periods_per_offering * company_stock_plan.offering_periods)

    # Change in time over each iteration
    dt = time_frame / steps

    prices = np.zeros((simulations, steps + 1))
    prices[:, 0] = company_stock_start_parameters.initial_price

    for t in range(1, steps + 1):
        z = np.random.standard_normal(simulations)  # random variable
        # Monte Carlo formula: S(t+1) = S(t) * exp((r - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * z)
        prices[:, t] = (
            prices[:, t - 1] *
            np.exp(
                (company_stock_start_parameters.expected_rate_of_return - 0.5 * company_stock_start_parameters.volatility**2) * dt + 
                company_stock_start_parameters.volatility * np.sqrt(dt) * z
            )
        )
    if file_name is None or len(file_name) == 0:
        file_name = f'prices_{company_stock_plan.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    np.savetxt(f'{file_name}.csv', prices, delimiter=',')
    return prices