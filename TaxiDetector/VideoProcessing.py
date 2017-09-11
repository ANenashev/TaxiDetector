#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from sklearn.metrics.pairwise import euclidean_distances
import os
from sklearn.cluster import KMeans

'''
Функция обработки кадра изображения.
Входные параметры:
    frame - кадр
    color_sample - образец цвета, который нужно найти в кадре, np.array([1,3])
    center - список центров кластеров, np.array([n_clusters,3])
Выходные параметры:
    frame - обработанный кадр
    color_sample - центр кластера, который оказался достаточно близко к образцу, np.array([1,3])
    center - список центров кластеров, np.array([n_clusters,3])
'''
def ProcessFrame(frame, color_sample, center):
    
    #порог близости центра кластера к образцу
    color_threshold = 100
    #порог площади цветового пятна
    area_threshold = 500

    #преобразуем входное изображение в двумерный float массив
    Z = frame.reshape((-1,3))    
    Z = np.float32(Z)

    #количество кластеров
    K = 8
    
    #если центры кластеров не заданы, проинициализируем их и обработаем кадр
    if (center is None):
        kmeans = KMeans(n_clusters = K, init='k-means++', n_init = 10, n_jobs=-2, max_iter=100, random_state=241).fit(Z)
    #если получены центры с предыдущего кадра, используем их
    else:
        kmeans = KMeans(n_clusters = K, init=center, n_init = 1, max_iter=100, random_state=241).fit(Z)

    #преобразуем полученые центры в (B,G,R)-массивы
    center = np.uint8(kmeans.cluster_centers_)
    #метки кластеров для каждого пикселя исходного изображения
    label = kmeans.labels_
    
    #определим расстояния между векторами центров кластеров и вектором образце цвета
    dists = euclidean_distances(center, color_sample)

    #сохраняем метку наиболее близкого к образцу центра
    color_label = dists.argmin()

    #черная заливка
    res = np.zeros([label.shape[0], 3])

    #если ближайший центр кластера достаточно близок к образцу, продолжаем обработку изображения
    #иначе считаем, что в текущем кадре нет нужного цвета
    if (dists.min() < color_threshold):

        #присваиваем образцу центр отобранного кластера, чтобы использовать его в качестве образца для следующего кадра  
        color_sample = center[color_label]
        
        #заполняем пиксели, попавшие в выбраный кластер белыми точками на черном фоне        
        res[np.argwhere(label.flatten() == color_label)] = np.array([[255,255,255]])

        #теперь можно определить контуры желтых пятен на изображении
        #преобразуем его в монохромную картинку        
        res2 = res.reshape((frame.shape)).astype(np.uint8)
        res2 = cv2.cvtColor(res2,cv2.COLOR_BGR2GRAY)

        #ищем контуры
        contours = cv2.findContours(res2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        #проверим все получившиеся контуры и если контур достаточно велик, чтобы считать его автомобилем,
        #отметим его на изображении
        for cnt in contours[1]:
            if (cv2.contourArea(cnt) > area_threshold):                
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    else:
        #если мы не нашли достаточно близкого к образцу цвета,
        #принудительно зададим в качестве одного из центров кластеров этот самый образец,
        #тогда алгоритм точно попытается найти этот цвет на следующем кадре
        center[color_label] = color_sample
                
    return(frame, color_sample, center)


'''
Функция обработки видео из файла.
Входные параметры:
    source - путь к файлу-источнику
    dest - путь к выходному файлу
'''
def ProcessVideo(source, dest):

    source_path = os.path.abspath(source)
    dest_path = os.path.abspath(dest)

    #проверяем наличие входного файла
    if os.path.exists(source_path):
        #создаем объект видеозахвата
        cap = cv2.VideoCapture(source_path)
    else:            
        print("Can't open file", source_path)
        return
    
    #видеокодек для формирования выходного файла
    #на разных системах возможно нужны разные кодеки
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    
    #объект для записи видео
    #параметры изображения берем из входного видео
    out_video = cv2.VideoWriter(dest_path, fourcc, int(cap.get(cv2.CAP_PROP_FPS)), 
                                (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    #образец желтого цвета
    #это усредненные значения образцов цветов желтых такси с 50 различных изображений
    color_sample = np.array([[64,198,255]])

    #начальные значения центров
    init_centers = None
    
    while(1):
        #читаем кадр
        ret ,frame = cap.read()

        if ret == True:
            #обрабатываем его
            #здесь не используется обновление образца цвета
            #образец всегда один и тот же
            out_img, _, init_centers = ProcessFrame(frame, color_sample, init_centers)
            
            #демонстрируем получившийся кадр и записываем его в выходной файл
            cv2.imshow('Last processed frame',out_img)
            out_video.write(out_img)
            
            #нажав Esc можно прервать процедуру
            k = cv2.waitKey(60) & 0xff
            if k == 27:
                break

        else:
            break

    cv2.destroyAllWindows()
    cap.release()
    return


