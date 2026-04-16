from flask import Flask, render_template, send_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Parámetros
perfiles = [12.2, 32, 64]
velocidades = [3, 15, 50]
factores_actividad = [0.4, 0.5, 0.6, 0.7]
W = 3.84e6  # Hz
eta = 0.7  # umbral carga
f_inter = 0.5  # factor interferencia
eb_no_base = 5  # dB

def nmax(perfil, velocidad, factor_actividad, eb_no):
    R = perfil * 1000
    carga_por_usuario = eb_no * (R / W) * (1 + f_inter) * factor_actividad
    return int(eta / carga_por_usuario)

def calcular_resultados():
    results = []
    for p in perfiles:
        for v in velocidades:
            for fa in factores_actividad:
                n = nmax(p, v, fa, eb_no_base)
                results.append((p, v, fa, n))
    df = pd.DataFrame(results, columns=['Perfil', 'Velocidad', 'Factor_Actividad', 'Nmax'])
    return df

@app.route('/')
def index():
    df = calcular_resultados()
    # Crear gráfica
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    # Nmax vs Velocidad
    for p in perfiles:
        subset = df[df['Perfil'] == p].groupby('Velocidad')['Nmax'].mean()
        ax[0].plot(subset.index, subset.values, marker='o', label=f'Perfil {p} kb/s')
    ax[0].set_xlabel('Velocidad (km/h)')
    ax[0].set_ylabel('Nmax')
    ax[0].set_title('Nmax vs Velocidad')
    ax[0].legend()
    ax[0].grid(True)
    
    # Nmax vs Factor de Actividad
    for p in perfiles:
        subset = df[df['Perfil'] == p].groupby('Factor_Actividad')['Nmax'].mean()
        ax[1].plot(subset.index, subset.values, marker='s', label=f'Perfil {p} kb/s')
    ax[1].set_xlabel('Factor de Actividad')
    ax[1].set_ylabel('Nmax')
    ax[1].set_title('Nmax vs Factor de Actividad')
    ax[1].legend()
    ax[1].grid(True)
    
    plt.tight_layout()
    image_path = 'static/plot.png'
    plt.savefig(image_path)
    plt.close()
    
    # Convertir df a HTML
    table_html = df.to_html(index=False)
    
    return render_template('index.html', table=table_html, image=image_path)

if __name__ == '__main__':
    app.run(debug=True)