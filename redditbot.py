import praw
import json
import requests
import tweepy
import time
import os
import urllib.parse
from glob import glob
import sys
import config
#config es un archivo python con las credenciales de la cuenta de reddit en la que corre la app.


ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

#Subreddit del que recogerá los datos
NOMBRESUBREDDIT = ''
#Ruta donde se descargarán las imágenes de los posts
IMGDIR = 'img'
#Fichero donde se va añadiendo los posts que se tuitean para evitar duplicados
LOG = 'log.txt'

def conexionreddit():

        print('[bot] Conectando bot a reddit...')
        redditConnection = praw.Reddit(username=config.username,
                                        password=config.password,
                                        client_id=config.client_id,
                                        client_secret=config.client_secret,
                                        user_agent='Terraria reddit to twitter bot')
        return redditConnection

#Recoge los 5 pots en hot del reddit seleccionado. Si no puede tuitear ninguno, termina.
def posts(reddit):

        subreddit = reddit.subreddit(NOMBRESUBREDDIT)
        print('Posts seleccionados: ')
        contador = 0
        for submission in subreddit.hot(limit=5):
                postid = submission.id
                titulopost = submission.title
                urlpost = submission.url
                print (postid + ' - ' + titulopost + ' - ' + urlpost)
                crearTweet(postid, titulopost, urlpost)
                contador += 1
                if contador == 5:
                        print('Ninguno de los posts se puede tuitear. Se para el bot')
                        borraImg()
                        exit(0)

def crearTweet(postid, titulopost, urlpost):

        if not repetido(postid):
                imagen = convertirImagen(urlpost)
                if imagen == False:
                        print('Al no ser una imagen, no se tuitea')
                else:
                        publicarTweet(titulopost, imagen, postid)
        else:
                print('Post ya tuiteado')

#Comprueba si un post ya ha sido tuiteado
def repetido(postid):

        repetido = False
        with open(LOG, 'r') as log:
                for linea in log:
                        if postid in linea:
                                repetido = True
                                break
        return repetido

#convertirImagen() comprueba si la url a la que apunta el post es una imagen, si es así, la descarga a la ruta 'img'.
#Esta función devuelve el string de la ruta + la imagen. Ejemplo: img/q3588wtf.png
def convertirImagen(urlpost):

        if ('imgur.com' in urlpost) or ('i.redd' in urlpost):
                print ('La url del post es una imagen')
                nombreImg = os.path.basename(urllib.parse.urlsplit(urlpost).path)
                rutaImg = str(IMGDIR + '/' + nombreImg)
                print('[bot] Descargando la imagen de la url ' + urlpost + ' a la ruta ' + rutaImg)
                request = requests.get(urlpost, stream=True)
                if request.status_code == 200:
                        with open(rutaImg, 'wb') as ficheroImg:
                                for chunk in request:
                                        ficheroImg.write(chunk)
                        return rutaImg

        else:
                print('La url del post no es una imagen')
                return False

#Se loguea a twitter con tweepy y tuitea el titulo junto con la imagen
def publicarTweet(titulopost, imagen, postid):

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        print('Tuiteando post: ' + titulopost + ' con imagen: ' + imagen)
        log_postid(postid)
        if imagen:
                api.update_with_media(filename=imagen, status=titulopost)
                borraImg()
                exit(0)

#añade un post al log (tuiteado) para evitar duplicados
def log_postid(postid):
        with open(LOG, 'a') as out_file:
                out_file.write(str(postid) + '\n')

#Borra las imagenes de /img
def borraImg():

        for filename in glob(IMGDIR + '/*'):
                os.remove(filename)

def main():

        #Crea el directorio de imagen y/o el log si no existen.
        if not os.path.exists(LOG):
                with open(LOG, 'w'):
                        pass
        if not os.path.exists(IMGDIR):
                os.makedirs(IMGDIR)
                
        #Se conecta a reddit
        reddit = conexionreddit()
        print('[bot] Bot conectado!')
        
        #Coje los 5 primeros posts en hot y tuitea el primero que no haya tuiteado ya.
        posts(reddit)

main()
