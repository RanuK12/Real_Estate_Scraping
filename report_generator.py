import json, pathlib, pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

DATA_PATH = pathlib.Path(__file__).parent / "data" / "market_data.json"
TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def aggregate(df):
    # compute price per m2
    df['precio_m2'] = df['precio'] / df['superficie']
    # ensure date ordering
    df['fecha'] = pd.to_datetime(df['fecha'])
    # sort by zona and fecha
    df = df.sort_values(['zona', 'fecha'])
    # group by zona
    grouped = df.groupby('zona')
    # compute metrics
    summary = []
    for zona, group in grouped:
        precio_m2_mean = group['precio_m2'].mean()
        stock = group.shape[0]
        # variation %: (latest - earliest) / earliest * 100
        if len(group) >= 2:
            earliest = group.iloc[0]['precio_m2']
            latest = group.iloc[-1]['precio_m2']
            variacion = (latest - earliest) / earliest * 100
        else:
            variacion = 0.0
        summary.append({
            'zona': zona,
            'precio_m2_mean': round(precio_m2_mean, 2),
            'stock': stock,
            'variacion': round(variacion, 2)
        })
    result_df = pd.DataFrame(summary)
    return result_df

def render_pdf(df, out_path):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    tmpl = env.get_template("report.html")
    html = tmpl.render(tabla=df.to_dict(orient="records"))
    HTML(string=html).write_pdf(out_path)

if __name__ == "__main__":
    raw = load_data()
    df = pd.DataFrame(raw)
    summary = aggregate(df)
    out_file = pathlib.Path(__file__).parent / "output" / "informe.pdf"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    render_pdf(summary, out_file)
    print(f"✅ PDF generado: {out_file}")
