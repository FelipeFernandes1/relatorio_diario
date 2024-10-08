# -*- coding: utf-8 -*-
"""relatorio_diario.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Gz2avE0X890iA6Ue2WaWcRnP34-yW6Z0
"""

def relatorio_diario():
  #BIBLIOTECAS
  import pandas as pd
  import warnings
  from fpdf import FPDF
  from matplotlib.dates import DateFormatter
  warnings.filterwarnings("ignore")
  from datetime import datetime
  from google.colab import files
  import matplotlib.pyplot as plt
  import numpy as np
  
  #FUNÇAO PARA VERIFICAR O ARQUIVO CARREGADO
  def verificar_upload(base_nome):
    print(f"Faça o upload da base {base_nome}")
    uploaded_files = files.upload()  # Retorna um dicionário
    if not uploaded_files:
        return None  # Retorna None para indicar que nenhum upload foi feito
    file_name = next(iter(uploaded_files))  # Obtém o nome do primeiro arquivo carregado
    df = pd.read_excel(file_name, header = 3)  # Carrega o arquivo em um DataFrame (ajuste para pd.read_excel se for um Excel)
    if len(df) == 10000:  # Se a base for igual a 10000, é um indício de que haverá casos faltando
        print("ATENÇÃO, o tamanho da base é 10000 (limite Hugme)!")
    print("")
    colunas = ['Id HugMe', 'Data Reclamação', 'Status Hugme', 'Atribuido Para', 'Moderação status', 'Moderação motivo']
    # Verificando se todas as colunas necessárias estão presentes
    if not all(col in df.columns for col in colunas):
        print("Faltam algumas colunas necessárias, extraia um novo arquivo. A função será encerrada.")
        return None  # Retorna None ou poderia usar um erro aqui se preferir
    return df

  #CARREGANDO AS BASES(utilizando a função acima)
  colunas = ['Id HugMe', 'Data Reclamação', 'Status Hugme', 'Atribuido Para', 'Moderação status', 'Moderação motivo']
  df_Geral = pd.DataFrame(columns=colunas + ['Página'])
  # Verifica cada upload, aplica o filtro das colunas, cria o atributo página
  df_Classificados = verificar_upload("OLX")
  if df_Classificados is not None:
      df_Classificados = df_Classificados[colunas]
      df_Classificados['Página'] = 'Classificados'
      df_Geral = pd.concat([df_Geral, df_Classificados], axis=0)
  df_Pay = verificar_upload("Pay")
  if df_Pay is not None:
      df_Pay = df_Pay[colunas]
      df_Pay['Página'] = 'Pay'
      df_Geral = pd.concat([df_Geral, df_Pay], axis=0)
  df_Zap = verificar_upload("Zap")
  if df_Zap is not None:
      df_Zap = df_Zap[colunas]
      df_Zap['Página'] = 'Zap'
      df_Geral = pd.concat([df_Geral, df_Zap], axis=0)
  df_Viva = verificar_upload("Viva")
  if df_Viva is not None:
      df_Viva = df_Viva[colunas]
      df_Viva['Página'] = 'Viva'
      df_Geral = pd.concat([df_Geral, df_Viva], axis=0)
  df_Geral.reset_index(inplace=True, drop=True) # resetando o índice

  #LIMPEZA DAS BASES
  #tratando os valores de data
  df_Geral['Data Reclamação'] = df_Geral['Data Reclamação'].dt.date
  #tratando a coluna "atribuído para"
  df_Geral.loc[df_Geral['Atribuido Para'].isnull(), 'Atribuido Para'] = 'Sem atribuição'
  df_Geral.loc[df_Geral['Atribuido Para'] != 'Sem atribuição', 'Atribuido Para'] = 'Atribuído'
  df_Geral.rename(columns={'Atribuido Para': 'Status'}, inplace=True)
  #excluindo as reclamações a serem moderadas p página correta
  df_Geral = df_Geral.loc[~((df_Geral['Moderação motivo']=='A reclamação de outra empresa')&(df_Geral['Moderação status']=='Pendente'))]
  df_Geral.reset_index(inplace=True, drop=True)

  #GRÁFICOS E CONFIGURAÇÃO DO RELATÓRIO
  # Função para obter a data mínima formatada ou 'Não há' para o status especificado
  def get_last_date(df, status, status_hugme, pagina):
      filtered_df = df[
          (df['Status'] == status) &
          (df['Status Hugme'] == status_hugme) &
          (df['Página'] == pagina)
      ]
      if not filtered_df.empty:
          return filtered_df['Data Reclamação'].min().strftime('%d/%m')
      else:
          return 'Não há'
  # Função para gerar gráfico de casos pendentes
  def plot_pending_cases(df, paginas):
      pending_data = {
          "Página": [],
          "Sem atribuição": [],
          "Atribuído": []
      }
      for pagina in paginas:
          # Filtra os chamados pendentes (Status Hugme = 'Novo')
          df_pendentes = df[(df['Status Hugme'] == 'Novo') & (df['Página'] == pagina)]
          sem_atribuicao = df_pendentes[df_pendentes['Status'] == 'Sem atribuição'].shape[0]
          atribuido = df_pendentes[df_pendentes['Status'] == 'Atribuído'].shape[0]
          pending_data["Página"].append(pagina)
          pending_data["Sem atribuição"].append(sem_atribuicao)
          pending_data["Atribuído"].append(atribuido)
      # Criar DataFrame e ordenar
      df_pending = pd.DataFrame(pending_data)
      df_pending.set_index('Página', inplace=True)
      df_pending['Total'] = df_pending['Sem atribuição'] + df_pending['Atribuído']
      df_pending_sorted = df_pending.sort_values(by='Total', ascending=True)  # Ordenar de forma crescente
      # Definir as cores das barras
      colors = ['#808080', '#ec7b20']  # Cinza claro para 'Sem atribuição' e roxo para 'Atribuído'
      # Plotting
      fig, ax = plt.subplots(figsize=(9, 2))
      bars = df_pending_sorted[['Atribuído', 'Sem atribuição']].plot(kind='barh', stacked=True, ax=ax, width=0.9, color=colors)
      # Ajustar fontes dos ticks
      ax.tick_params(axis='x', labelsize=10)
      ax.tick_params(axis='y', labelsize=10)
      # Remover o título do eixo y
      ax.set_ylabel('')  # Remove o título do eixo y
      # Adicionar os números correspondentes a cada barra
      for i, (sem_atribuicao, atribuido) in enumerate(zip(df_pending_sorted['Sem atribuição'], df_pending_sorted['Atribuído'])):
          total = sem_atribuicao + atribuido
          if total >= 15:  # Mostrar os números apenas se o total for maior ou igual a 15
              ax.annotate(f'{atribuido}',
                          xy=(atribuido, i),
                          xytext=(-10, 0),
                          textcoords='offset points',
                          ha='center',
                          va='center',
                          fontsize=10,
                          color='white')
              ax.annotate(f'{sem_atribuicao}',
                          xy=(atribuido + sem_atribuicao, i),
                          xytext=(-10, 0),
                          textcoords='offset points',
                          ha='center',
                          va='center',
                          fontsize=10,
                          color='black')
      plt.tight_layout()
      plt.savefig('casos_pendentes.png')
      plt.close()
  # Função para gerar gráfico de média diária acumulada
  def plot_cumulative_daily_average(df, paginas):
      plt.figure(figsize=(9, 4))  # Aumentando o tamanho vertical do gráfico
      max_y_value = 0  # Variável para rastrear o valor máximo no eixo Y
      # Definindo marcadores para as linhas
      markers = ['o', 's', '>', '_']  # Círculo, quadrado, triângulo para cima, diamante
      color = '#5800d9'
      for i, pagina in enumerate(paginas):
          df_pagina = df[df['Página'] == pagina].set_index('Data Reclamação').resample('D').size()
          dates = df_pagina.index
          values = df_pagina.values
          if len(values) == 0:
              continue  # Pular caso não haja dados para essa página
          # Calcular a média acumulada
          cumulative_sum = np.cumsum(values)
          cumulative_days = np.arange(1, len(values) + 1)
          cumulative_average = cumulative_sum / cumulative_days
          plt.plot(dates[:len(cumulative_average)], cumulative_average,
                  label=f'{pagina}',
                  linewidth=2,
                  color=color,        # Definindo a cor para todas as linhas
                  marker=markers[i % len(markers)])  # Aplica marcador
          # Adicionar médias acima dos pontos com tamanho de fonte ajustado
          for date, avg in zip(dates[:len(cumulative_average)], cumulative_average):
            if avg >= 5:  # Verifica se a média é maior ou igual a 5
              plt.text(date, avg + 1, f'{int(avg)}', fontsize=8, ha='center', va='bottom', color='#5800d9')  # Ajuste o fontsize aqui
          # Atualiza o valor máximo encontrado no eixo Y, se houver valores em cumulative_average
          if cumulative_average.max() > max_y_value:
              max_y_value = cumulative_average.max()
      # Garantir que o gráfico só seja gerado se houver dados
      if max_y_value > 0:
          # Adicionar uma margem de 10% ao valor máximo do eixo Y
          ylim_upper = max_y_value * 1.4
          plt.ylim(0, ylim_upper)
      plt.legend(loc='upper right', fontsize=8, framealpha=0.6)
      plt.gca().xaxis.set_major_formatter(DateFormatter('%d/%m'))  # Formatar datas no eixo X
      # Ajustar fontes dos ticks
      plt.xticks(fontsize=10)
      plt.yticks(fontsize=10)
      plt.tight_layout()
      plt.savefig('media_diaria_acumulada.png')
      plt.close()
  # Função para gerar relatório em PDF
  def generate_pdf_report(data_ultimas_datas, resultados_dia_anterior, resultados_ultimos_dias, resultados_qtd_dias_presentes, img_path, media_diaria_acumulada_img_path):
      pdf = FPDF()
      pdf.add_page()
      # Largura da página e cálculo do ponto central
      page_width = pdf.w - 2 * pdf.l_margin  # Largura da página (menos as margens)
      # Título do relatório
      pdf.set_font("Arial", style='B', size=16)
      pdf.cell(200, 10, txt=f"Relatório diário", ln=True, align="C")
      pdf.ln(-5)  # Ajustar o espaçamento
      # Subtítulo
      pdf.set_font("Arial", size=10)  # Defina a fonte para o subtítulo
      pdf.cell(200, 10, txt=f"Casos criados entre as datas {df_Geral['Data Reclamação'].min().strftime('%d/%m')} e {df_Geral['Data Reclamação'].max().strftime('%d/%m')}", ln=True, align="C")  # Adicione seu subtítulo aqui
      # Seção 1: Gráfico de Casos Pendentes
      # Título "Casos pendentes de resposta pública" (centralizado, sem negrito)
      pdf.set_font("Arial", size=13)
      title_text = "Casos pendentes de resposta pública"
      title_width = pdf.get_string_width(title_text)
      pdf.set_x((page_width - title_width) / 2 + pdf.l_margin)
      pdf.cell(title_width, 30, txt=title_text, ln=True, align="C")
      pdf.image(img_path, x=4, y=pdf.get_y() + -13, w=190)
      pdf.ln(30)  # Ajustar o espaçamento entre o gráfico e a tabela
      # Seção 2: Últimas Datas dos Chamados (em formato de tabela)
      # Título "Últimas datas dos casos pendentes" (centralizado, sem negrito)
      title_text = "Últimas datas dos casos pendentes"
      title_width = pdf.get_string_width(title_text)
      pdf.set_x((page_width - title_width) / 2 + pdf.l_margin)
      pdf.cell(title_width, 10, txt=title_text, ln=True, align="C")
      # Largura das colunas
      col_width = 150 / 3  # Três colunas com larguras iguais
      # Cabeçalho da tabela (centralizado)
      pdf.set_font("Arial", style='B', size=10)
      pdf.set_x(30)  # Centraliza a tabela
      pdf.cell(col_width, 7, txt="Página", border=1, align="C")
      pdf.cell(col_width, 7, txt="Sem atribuição", border=1, align="C")
      pdf.cell(col_width, 7, txt="Atribuído", border=1, ln=True, align="C")
      # Adicionando os dados na tabela (centralizado)
      pdf.set_font("Arial", size=10)
      for item in data_ultimas_datas:
          pagina, datas = item.split(" Sem atribuição: ")
          sem_atribuicao, atribuido = datas.split(", Atribuído: ")
          pdf.set_x(30)  # Centraliza a tabela
          pdf.cell(col_width, 7, txt=pagina, border=1, align="C")
          pdf.cell(col_width, 7, txt=sem_atribuicao, border=1, align="C")
          pdf.cell(col_width, 7, txt=atribuido, border=1, ln=True, align="C")
      pdf.ln(5)  # Ajustar o espaçamento após a tabela
      # Seção 3: Gráfico de Média Diária Acumulada
      # Título "Média diária acumulada do incoming" (centralizado, sem negrito)
      pdf.set_font("Arial", size=13)
      title_text = "Incoming(média diária acumulada)"
      title_width = pdf.get_string_width(title_text)
      pdf.set_x((page_width - title_width) / 2 + pdf.l_margin)
      pdf.cell(title_width, 10, txt=title_text, ln=True, align="C")
      pdf.image(media_diaria_acumulada_img_path, x=8, y=pdf.get_y() -2, w=190)
      pdf.ln(95)  # Ajustar o espaçamento após o gráfico
      # Gerar o PDF
      pdf.output("relatorio.pdf")
  # Parâmetros
  status_sem_atribuicao = 'Sem atribuição'
  status_atribuido = 'Atribuído'
  status_hugme = 'Novo'
  paginas = ['Pay', 'Classificados', 'Zap', 'Viva']
  # Obter as últimas datas
  data_ultimas_datas = []
  for pagina in paginas:
      ultimo_sem_atribuicao = get_last_date(df_Geral, status_sem_atribuicao, status_hugme, pagina)
      ultimo_atribuido = get_last_date(df_Geral, status_atribuido, status_hugme, pagina)
      data_ultimas_datas.append(f"{pagina} Sem atribuição: {ultimo_sem_atribuicao}, Atribuído: {ultimo_atribuido}")
  # Gerar o gráfico dos casos pendentes
  plot_pending_cases(df_Geral, paginas)
  # Cálculo das médias e contagem do dia anterior
  df_Geral['Data Reclamação'] = pd.to_datetime(df_Geral['Data Reclamação'])
  # Dicionários para armazenar os resultados
  resultados_dia_anterior = {}
  resultados_ultimos_dias = {}
  resultados_qtd_dias_presentes = {}
  # Função para calcular a contagem do dia anterior e a média diária para uma página específica
  def calcular_medias_por_pagina(df, pagina):
      df_pagina = df[df['Página'] == pagina].copy()
      if df_pagina.empty:
          return 0, 0, 0  # Retorna 0 se não houver dados para a página
      ultimo_dia = df_pagina['Data Reclamação'].max()
      dia_anterior = ultimo_dia - pd.DateOffset(days=1)
      # Contagem do dia anterior
      contagem_dia_anterior = df_pagina[df_pagina['Data Reclamação'] == dia_anterior].shape[0]
      # Calcular a média diária baseada nos dias presentes no relatório
      dias_presentes = df_pagina.set_index('Data Reclamação').resample('D').size()
      num_dias_presentes = dias_presentes.shape[0]
      if num_dias_presentes > 0:
          media_diaria = dias_presentes.mean()
      else:
          media_diaria = 0  # Se não houver dados, define como 0
      return contagem_dia_anterior, media_diaria, num_dias_presentes
  # Calcular e armazenar os resultados para cada página
  for pagina in paginas:
      contagem_dia_anterior, media_diaria, qtd_dias_presentes = calcular_medias_por_pagina(df_Geral, pagina)
      resultados_dia_anterior[pagina] = contagem_dia_anterior
      resultados_ultimos_dias[pagina] = media_diaria
      resultados_qtd_dias_presentes[pagina] = qtd_dias_presentes
  # Gerar gráficos
  plot_cumulative_daily_average(df_Geral, paginas)
  plot_pending_cases(df_Geral, paginas)
  # Gerar o relatório PDF
  generate_pdf_report(data_ultimas_datas, resultados_dia_anterior, resultados_ultimos_dias, resultados_qtd_dias_presentes, 'casos_pendentes.png', 'media_diaria_acumulada.png')
