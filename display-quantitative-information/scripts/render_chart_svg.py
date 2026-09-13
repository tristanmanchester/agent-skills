#!/usr/bin/env python3
"""Render explicit first-pass SVG charts without implicit aggregation or time warping."""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import html
import json
import math
from pathlib import Path
import sys


def number(value: str, *, allow_missing: bool = False) -> float | None:
    if not isinstance(value, str):
        raise ValueError('Expected a CSV text value')
    if not value.strip():
        if allow_missing:
            return None
        raise ValueError('Missing numeric value')
    try:
        result = float(value)
    except ValueError as error:
        raise ValueError('Expected an explicit numeric value; normalise locale formatting first') from error
    if not math.isfinite(result):
        raise ValueError('Non-finite numbers are not plottable observations')
    return result


def date_number(value: str) -> float:
    # Deliberately unambiguous ISO calendar dates, not locale-dependent date guessing.
    parsed = dt.date.fromisoformat(value)
    if value != parsed.isoformat():
        raise ValueError('Dates must be YYYY-MM-DD')
    return float(parsed.toordinal())


def extent(values: list[float], zero: bool = False) -> tuple[float, float]:
    low, high = min(values), max(values)
    if zero:
        low, high = min(0.0, low), max(0.0, high)
    if low == high:
        padding = abs(low) * 0.05 or 1.0
        return low - padding, high + padding
    if zero:
        return low, high
    span = high - low
    if not math.isfinite(span):
        raise ValueError('Numeric range is too large; rescale units before plotting')
    return low - span * 0.05, high + span * 0.05


def render(rows: list[dict[str, str]], *, x: str, y: str, chart: str,
           group: str | None = None, x_type: str = 'number', title: str = '',
           width: int = 900, height: int = 520) -> tuple[str, dict]:
    if chart not in {'bar', 'dot', 'line', 'scatter'}:
        raise ValueError('Choose bar, dot, line, or scatter explicitly')
    if x_type not in {'number', 'date'}:
        raise ValueError('x_type must be number or date')
    if type(width) is not int or type(height) is not int or not 400 <= width <= 4000 or not 300 <= height <= 4000:
        raise ValueError('Width must be 400..4000 and height 300..4000')
    if not rows or len(rows) > 10000:
        raise ValueError('Supply 1..10000 rows; larger data needs an appropriate plotting pipeline')
    required = [x, y] + ([group] if group else [])
    if any(any(column not in row for column in required) for row in rows):
        raise ValueError('A selected CSV column is missing')
    points = []
    for index, row in enumerate(rows, 1):
        label, series = row[x], row[group] if group else ''
        if not isinstance(label, str) or not label.strip() or not isinstance(series, str):
            raise ValueError(f'Invalid x/group value at data row {index}')
        coordinate = (date_number(label) if x_type == 'date' else number(label)) if chart in {'line', 'scatter'} else label
        value = number(row[y], allow_missing=chart == 'line')
        points.append({'x': coordinate, 'label': label, 'y': value, 'group': series})
    groups = list(dict.fromkeys(point['group'] for point in points))
    if len(groups) > 6:
        raise ValueError('More than six series needs a deliberate small-multiple or other design')
    if chart in {'bar', 'line'}:
        keys = [(point['group'], point['x']) for point in points]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate x within a series: choose and document aggregation before plotting')
    values = [point['y'] for point in points if point['y'] is not None]
    if not values:
        raise ValueError('No observed y values')
    ymin, ymax = extent(values, zero=chart == 'bar')
    if not math.isfinite(ymax-ymin) or not math.isfinite(ymin) or not math.isfinite(ymax):
        raise ValueError('Unrepresentable y range; rescale units')
    x0, x1, y0, y1 = 82.0, float(width-150 if group else width-30), 64.0, float(height-80)
    def sy(value):
        return y1 - (value-ymin)/(ymax-ymin)*(y1-y0)
    categories = list(dict.fromkeys(point['x'] for point in points)) if chart in {'bar', 'dot'} else []
    if len(categories) > 30:
        raise ValueError('More than 30 categories needs a different layout')
    xmin = xmax = None
    if categories:
        def sx(value):
            return x0 + (categories.index(value)+0.5)*(x1-x0)/len(categories)
    else:
        xmin, xmax = extent([point['x'] for point in points])
        if not math.isfinite(xmax-xmin) or not math.isfinite(xmin) or not math.isfinite(xmax):
            raise ValueError('Unrepresentable x range; rescale units')
        def sx(value):
            return x0 + (value-xmin)/(xmax-xmin)*(x1-x0)
    escape = lambda text: html.escape(str(text), quote=True)
    colours = ['#222222', '#0066aa', '#994400', '#337744', '#773399', '#665500']
    shapes = ['circle', 'square', 'triangle', 'diamond', 'plus', 'cross']
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
                f'<title id="title">{escape(title or y + " by " + x)}</title>',
                f'<desc id="desc">{escape(chart)} chart. No aggregation. {len(rows)} input rows; {len(values)} observations. Missing line values break the path. Consult the source data for exact values.</desc>',
                '<rect width="100%" height="100%" fill="white"/>']
    def text(px, py, content, anchor='middle', size=11):
        elements.append(f'<text x="{px:.4f}" y="{py:.4f}" text-anchor="{anchor}" font-size="{size}" font-family="sans-serif">{escape(content)}</text>')
    text(width/2, 28, title or f'{y} by {x}', size=16)
    text((x0+x1)/2, height-20, x)
    text(x0, 50, y, anchor='start')
    def tick_values(low, high):
        values = [low + (high-low)*(index/4) for index in range(5)]
        if len(set(values)) != len(values):
            raise ValueError('Axis resolution is insufficient; use an explicit offset or rescale the data')
        for precision in (5, 8, 12, 17):
            labels = [format(value, f'.{precision}g') for value in values]
            if len(set(labels)) == len(labels):
                return list(zip(values, labels))
        raise ValueError('Cannot label distinct axis values faithfully')
    for value, label in tick_values(ymin, ymax):
        yy = sy(value)
        elements.append(f'<line x1="{x0}" y1="{yy:.4f}" x2="{x1}" y2="{yy:.4f}" stroke="#dddddd"/>')
        text(x0-8, yy+4, label, anchor='end')
    if categories:
        ticks = [(sx(value), str(value)) for value in categories]
    elif x_type == 'date':
        # Actual observed dates; spacing remains proportional to elapsed days.
        coordinates = sorted(set(point['x'] for point in points))
        step = max(1, math.ceil(len(coordinates)/8))
        chosen = coordinates[::step]
        if coordinates[-1] not in chosen:
            chosen.append(coordinates[-1])
        ticks = [(sx(value), dt.date.fromordinal(int(value)).isoformat()) for value in chosen]
    else:
        ticks = [(sx(value), label) for value, label in tick_values(xmin, xmax)]
    for px, label in ticks:
        text(px, y1+22, label, size=10)
    def marker(px, py, series_index):
        colour, shape = colours[series_index], shapes[series_index]
        common = f'fill="{colour}" stroke="{colour}"'
        if shape == 'circle':
            elements.append(f'<circle cx="{px:.4f}" cy="{py:.4f}" r="3.5" {common}/>')
        elif shape == 'square':
            elements.append(f'<rect x="{px-3.5:.4f}" y="{py-3.5:.4f}" width="7" height="7" {common}/>')
        elif shape in {'triangle', 'diamond'}:
            vertices = [(px,py-4),(px+4,py+4),(px-4,py+4)] if shape == 'triangle' else [(px,py-4),(px+4,py),(px,py+4),(px-4,py)]
            elements.append('<polygon points="'+' '.join(f'{a:.4f},{b:.4f}' for a,b in vertices)+f'" {common}/>')
        else:
            pairs = [((px-4,py),(px+4,py)),((px,py-4),(px,py+4))] if shape == 'plus' else [((px-3,py-3),(px+3,py+3)),((px-3,py+3),(px+3,py-3))]
            for (a,b),(c,d) in pairs:
                elements.append(f'<line x1="{a:.4f}" y1="{b:.4f}" x2="{c:.4f}" y2="{d:.4f}" stroke="{colour}" stroke-width="2"/>')
    for index, series_name in enumerate(groups):
        series = [point for point in points if point['group']==series_name]
        if chart == 'line':
            series.sort(key=lambda point: point['x'])
            segments, current = [], []
            for point in series:
                if point['y'] is None:
                    if current:
                        segments.append(current); current=[]
                else:
                    current.append(point)
            if current:
                segments.append(current)
            for segment in segments:
                coords=' '.join(('M' if i==0 else 'L')+f" {sx(point['x']):.4f} {sy(point['y']):.4f}" for i,point in enumerate(segment))
                elements.append(f'<path d="{coords}" fill="none" stroke="{colours[index]}" stroke-width="1.5"/>')
        for point in series:
            if point['y'] is None:
                continue
            px, py = sx(point['x']), sy(point['y'])
            if chart == 'bar':
                barwidth=(x1-x0)/len(categories)*0.75/len(groups)
                px += (index-(len(groups)-1)/2)*barwidth
                zero=sy(0)
                elements.append(f'<rect x="{px-barwidth/2:.4f}" y="{min(py,zero):.4f}" width="{barwidth:.4f}" height="{abs(py-zero):.4f}" fill="{colours[index]}"/>')
            else:
                marker(px,py,index)
        if group:
            marker(x1+18,y0+index*22,index)
            text(x1+29,y0+index*22+4,series_name,anchor='start',size=10)
    elements.append('</svg>')
    return '\n'.join(elements)+'\n', {'chart':chart,'x_type':x_type if not categories else 'category',
        'aggregation':'none','rows_input':len(rows),'points_rendered':len(values),
        'missing_line_values':len(rows)-len(values),'x_domain':None if categories else [xmin,xmax],
        'y_domain':[ymin,ymax],'category_order':categories,
        'limits':'First-pass graphic. Inspect label fit, overlapping points, units, source, uncertainty, and accessibility before publication.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv',type=Path,required=True)
    parser.add_argument('--x',required=True); parser.add_argument('--y',required=True)
    parser.add_argument('--group'); parser.add_argument('--chart',choices=['bar','dot','line','scatter'],required=True)
    parser.add_argument('--x-type',choices=['number','date'],default='number')
    parser.add_argument('--title',default=''); parser.add_argument('--width',type=int,default=900); parser.add_argument('--height',type=int,default=520)
    parser.add_argument('--output',type=Path,required=True); parser.add_argument('--metadata',type=Path)
    args=parser.parse_args(argv)
    try:
        if args.csv.stat().st_size > 16*1024*1024:
            raise ValueError('CSV exceeds 16 MiB input limit')
        with args.csv.open(encoding='utf-8-sig',newline='') as stream:
            reader=csv.DictReader(stream)
            if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
                raise ValueError('CSV headers must be present and unique')
            rows=[]
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('CSV row width does not match header')
                rows.append(row)
                if len(rows)>10000:
                    raise ValueError('CSV exceeds 10000 rows')
        svg,metadata=render(rows,x=args.x,y=args.y,chart=args.chart,group=args.group,x_type=args.x_type,title=args.title,width=args.width,height=args.height)
        for target in [args.output]+([args.metadata] if args.metadata else []):
            if target.exists() or target.is_symlink():
                raise FileExistsError('Output paths must be new')
        if args.metadata and args.metadata.absolute()==args.output.absolute():
            raise ValueError('SVG and metadata need different output paths')
        with args.output.open('x',encoding='utf-8') as stream:
            stream.write(svg)
        if args.metadata:
            with args.metadata.open('x',encoding='utf-8') as stream:
                json.dump(metadata,stream,indent=2)
        print(json.dumps({'output':str(args.output),**metadata}))
    except (OSError,ValueError,TypeError,csv.Error) as error:
        print(json.dumps({'error':str(error)}),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
