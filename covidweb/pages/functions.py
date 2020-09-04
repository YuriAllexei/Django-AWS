import pandas as pd
import requests, json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
import datetime

token = '92170321-528f-f1dd-5d59-f8613e072746'
banxico_token = '7deb6f657b170b10ea009e84f6daf7346360a10fcbe2beaa53130542c3ad6283'
liga_base = 'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/'

## METODOS GENERALES API INEGI
def obtener_json(indicador,banco,localidad):
    global liga_base,token
    #if localidad.isdigit() is False: localidad = localidades_dict[localidad]
    indicador = indicador + '/'
    idioma = 'es/'
    banco = banco + '/2.0/'
    final_liga = str(token) + '?type=json'
    liga_api = liga_base + indicador + idioma + localidad + '/false/' + banco + final_liga
    req = requests.get(liga_api)
    data = json.loads(req.text)
    return data

def indicador_a_df(indicador,banco,localidad='0700'):
    data = obtener_json(indicador,banco,localidad)
    obs_totales = len(data['Series'][0]['OBSERVATIONS'])
    dic = {'fechas':[data['Series'][0]['OBSERVATIONS'][i]['TIME_PERIOD'] for i in range(obs_totales)],
            indicador:[float(data['Series'][0]['OBSERVATIONS'][i]['OBS_VALUE']) for i in range(obs_totales)]}
    df = pd.DataFrame.from_dict(dic)
    return df

def indicadores_a_df(indicadores,banco,localidades=['0700']):
    lista_df = []
    for i in range(len(indicadores)):
        indicador = indicadores[i]
        for localidad in localidades:
            df = indicador_a_df(indicador, banco, localidad)
            if i > 0: df = df.drop(['fechas'],axis=1)
            lista_df.append(df)
   
    df = pd.concat(lista_df,axis=1)
    return df    

def banxico_a_df(indicador):
    global banxico_token       
    liga_banxico = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
    req = requests.get(liga_banxico+indicador+'/datos',params={'token':banxico_token})
    data = json.loads(req.text)
    n = len(data['bmx']['series'][0]['datos'])
    dict_df = dict(fechas = [data['bmx']['series'][0]['datos'][i]['fecha'] for i in range(n)],
                    vals = [data['bmx']['series'][0]['datos'][i]['dato'] for i in range(n)])
    df = pd.DataFrame.from_dict(dict_df)
    df.index = pd.to_datetime(df.fechas,format='%d/%m/%Y')
    df = df.drop(['fechas'],axis=1)
    df.columns = [indicador]
    return df

def graficar_pib():
    indicadores = ['493911','493925','493932','493967']
    df = indicadores_a_df(indicadores,'BIE')
    df.columns = ['fechas','Total','Primario','Secundario','Terciario']
    df.index = pd.date_range(df.fechas.iloc[0],df.fechas.iloc[-1],periods=len(df.fechas))
    df = df.sort_index()
    vars = df[df.columns[1:]].pct_change()
    
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True)
    for i in range(1,len(df.columns)):
        leg_group = 'group{}'.format(i)
        col = df.columns[i]
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,legendgroup=leg_group,
                                line=dict(color=colors[i-1])),row=1,col=1)
    for i in range(len(vars.columns)):
        leg_group = 'group{}'.format(i+1)
        col = vars.columns[i]
        fig.add_trace(go.Scatter(x=vars.index,y=vars[col],legendgroup=leg_group,
                                line=dict(color=colors[i]),showlegend=False,
                                opacity=0.7),row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x', height=600,width=1200,
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=20,
                                        label="20 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all")
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=20,
                                        label="20 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all")
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))
    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True)
    fig.update_yaxes(title_text='PIB trimestral',row=1,col=1)
    fig.update_yaxes(zeroline=True,title_text='Variación (%)',row=1,col=2)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def graficar_inflacion():
    indicadores = ['628229','628230','628233','628231','628232','628234','628235']
    df = indicadores_a_df(indicadores,'BIE')
    df.columns = ['fechas','Índice general','Subyacente','No subyacente',
                    'Mercancias','Servicios','Agropecuarios',
                    'Energéticos y tarifas autorizadas por el gobierno']
    df.fechas = df.fechas.str.replace(r'(\d{4}/\d{2})/02',r'\1/15')
    df.index = pd.to_datetime(df.fechas,format='%Y/%m/%d')
    df = df.drop(['fechas'],axis=1)
    df = df[::-1].loc['2010':]
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True,shared_yaxes=True)
    for col in df.columns[:3]:
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,legendgroup=col,
                                opacity=0.6),row=1,col=1)
    for col in df.columns[3:]:
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col,
                                opacity=0.6),row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        legend=dict(orientation="h",yanchor='bottom'),
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=3,
                                        label="3 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))
    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True,zeroline = True)
    fig.update_yaxes(title_text='Inflación',row=1,col=1)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def graficar_tasas_interes():
    indicadores = ['SF61745','SF43783','SF43773','SF44073','SF43936']
    nombres = ['Tasa objetivio','TIIE a 28 días','Tasa de fondeo bancario','Mexibor a 3 meses','Cetes a 28 días']
    fig = px.line()
    for i in range(len(indicadores)):
        id = indicadores[i]
        df = banxico_a_df(id)
        df = df.loc['2005':]
        fig.add_scatter(x=df.index,y=df[id],mode='lines',name=nombres[i],opacity=0.7)
    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            )))
    fig.update_xaxes(showspikes = True)
    fig.update_yaxes(showspikes = True)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def graficar_tipo_cambio():
    indicadores = ['SF46405','SF46410','SF46406','SF46407','SF290383','SF46411']
    nombres = ['Dólar EUA','Euro','Yen japonés','Libra esterlina','Yuan chino',
                'Derecho Especial de Giro']
    fig = make_subplots(rows=1,cols=2,shared_xaxes=True)
    colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    for i in range(len(indicadores)):
        id = indicadores[i]
        df = banxico_a_df(id)
        df = df[df[id]!='N/E'].astype(float)
        df = df.loc['2005':]
        df['variacion'] = df.pct_change()
        fig.add_trace(go.Scatter(x=df.index,y=df[id],name=nombres[i],
                                legendgroup=nombres[i],line=dict(color=colors[i])),
                    row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df.variacion,name=nombres[i],
                                legendgroup=nombres[i],line=dict(color=colors[i]),
                                showlegend=False,opacity=0.5),
                    row=1,col=2)

    fig.update_layout(template='simple_white',
                        hovermode='x',height=600,width=1200,
                        legend=dict(orientation="h",yanchor='bottom'),
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all")
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"),
                        xaxis2=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                        label="1 año",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=5,
                                        label="5 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=10,
                                        label="10 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(count=15,
                                        label="15 años",
                                        step="year",
                                        stepmode="backward"),
                                    dict(step="all",
                                        label='Todo')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type="date"
                        ))

    fig.update_xaxes(showspikes = True,matches='x')
    fig.update_yaxes(showspikes = True)
    fig.update_yaxes(title_text='Tipo de cambio',row=1,col=1)
    fig.update_yaxes(title_text='Variación',row=1,col=2)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


