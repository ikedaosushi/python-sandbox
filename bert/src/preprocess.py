import cv2
import re
from base64 import b64encode
from os import makedirs
from os.path import join, exists
import json
import requests
from pathlib import Path
import pandas as pd
import MeCab
from gensim.models import KeyedVectors
import numpy as np
from urllib.request import urlretrieve
import unicodedata
import fasttext


class Load:
    def __init__(self, columns=["ID", "IndexedID",
                                "Enable", "Note",
                                "_A", "_B", "_C",
                                "A", "B", "C"]):
        self.columns = columns
        self.__raw_data = self.__raw_data()
        self.__enable_data = self.__enable_data()
        self.enable_data = \
            self.__enable_data.assign(AppealPoint=self.appeal_points())

    def __raw_data(self, path="..\\data\\raw\\data.csv"):
        return pd.read_csv(path, header=0, names=self.columns)

    def __enable_data(self):
        return self.__raw_data[self.__raw_data["Enable"] == 1]

    def pretrained(self, model="fasttext"):
        if model.lower() == "fasttext":
            path = "..\\data\\external\\cc.ja.300.bin"
            return fasttext.load_model(path)
        elif model.lower() == "word2vec":
            path = "..\\data\\external\\model.vec"
            return KeyedVectors.load_word2vec_format(path, binary=False)

    def ocr_text(self, path="..\\data\\interim\\ocr_text.json"):
        with open(path, "r") as f:
            text_dict = json.load(f)
        return text_dict

    def appeal_points(self):
        points = {}
        for idx, row in self.__enable_data.iterrows():
            points[idx] = []
            data_list = [row["A"], row["B"], row["C"]]
            for data in data_list:
                if "," not in data:
                    if int(data) == -1:
                        pass
                    elif int(data) not in points[idx]:
                        points[idx].append(int(data))
                else:
                    for point in data.split(","):
                        try:
                            if int(point) not in points[idx]:
                                points[idx].append(int(point))
                        except ValueError:
                            if len(point) == 0:
                                print(f"Number {idx} data is invalid shape.")
            points[idx].sort()

        points_list = []
        for value in points.values():
            points_list.append(value)

        return points_list

    def video_names(self):
        return [id+".mp4" for id in self.enable_data["IndexedID"]]

    def video_length(self, ocr_text: dict) -> list:
        return [len(value)-1 for value in ocr_text.values()]

    def stopwords(self, path="..\\data\\external\\stopword_ja.txt"):
        url = "http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
        if not exists(path):
            # Download the file from `url` and save it:
            urlretrieve(url, path)
        with open(path, "r", encoding="utf-8") as f:
            stopwords = f.read().split("\n")
        return stopwords


class Preprocess:
    def __init__(self, do_extract=False, do_ocr=False):
        self.load = Load()
        self.enable_data = self.load.enable_data

        if do_extract is True:
            video_names = self.load.video_names()
            for video_name in video_names:
                self.__save_frames(video_name)

        if do_ocr is True:
            self.ocr_text = self.__ocr_videos()
        else:
            self.ocr_text = self.load.ocr_text()

        self.enable_data["Text"] = self.__ocr_to_list(self.ocr_text)

        self.enable_data["VideoLength"] = self.load.video_length(self.ocr_text)

        print("Start loading a model of word2vec.")
        self.model = self.load.pretrained()
        print("Finish Loading.")

    def __save_frames(self, video_name: str,
                      dir_video="..\\data\\raw\\video\\",
                      dir_frame='..\\data\\interim\\frame\\',
                      name='image', ext='jpg', v_ext="mp4"):
        video_path = dir_video + video_name
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return

        dir_frame = dir_frame + re.sub(r'.*\\', '',
                                       re.sub(rf'\.{v_ext}', '',
                                              video_path))
        makedirs(dir_frame, exist_ok=True)
        base_path = join(dir_frame, name)

        idx = 0
        while cap.isOpened():
            idx += 1
            ret, frame = cap.read()
            if ret:
                if cap.get(cv2.CAP_PROP_POS_FRAMES) == 1:  # 0秒のフレームを保存
                    cv2.imwrite('{}_{}.{}'.format(base_path, "0000", ext),
                                frame)
                elif idx < cap.get(cv2.CAP_PROP_FPS):
                    continue
                else:  # 1秒ずつフレームを保存
                    second = int(cap.get(cv2.CAP_PROP_POS_FRAMES)/idx)
                    filled_second = str(second).zfill(4)
                    cv2.imwrite('{}_{}.{}'.format(base_path,
                                                  filled_second,
                                                  ext),
                                frame)
                    idx = 0
            else:
                break

    def __make_image_data_list(self, image_filenames):
        img_requests = []
        for imgname in image_filenames:
            with open(imgname, 'rb') as f:
                ctxt = b64encode(f.read()).decode()
                img_requests.append({
                        'image': {'content': ctxt},
                        'features': [{
                            'type': 'TEXT_DETECTION',
                            'maxResults': 1
                        }]
                })
        return img_requests

    def __make_image_data(self, image_filenames):
        imgdict = self.make_image_data_list(image_filenames)
        return json.dumps({"requests": imgdict}).encode()

    def __request_ocr(self, api_key, image_filenames):
        ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
        response = requests.post(ENDPOINT_URL,
                                 data=self.make_image_data(image_filenames),
                                 params={'key': api_key},
                                 headers={'Content-Type': 'application/json'})
        return response

    def __get_ocr_text(self, dir_frame: str, base_dir="",
                       path="..\\config\\key.json") -> str:
        with open(path) as f:
            api_key = json.load(f)["API_KEY"]

        image_filenames = list(Path(dir_frame).glob("*"))

        STEP = 10
        ocr_text = {}
        for idx in range(0, len(image_filenames), STEP):
            if idx == len(image_filenames):
                break
            else:
                response = self.request_ocr(api_key,
                                            image_filenames[idx:idx+STEP])
                if response.status_code != 200 or response.json().get('error'):
                    print(response.text)
                else:
                    res = response.json()['responses']
                    text_list = []
                    for resp in res:
                        try:
                            desc = resp['textAnnotations'][0]['description']
                            text_list.append(desc)
                        except KeyError:
                            text_list.append("")
                    for i, text in enumerate(text_list):
                        ocr_text[idx+i] = text
        return ocr_text

    def __ocr_videos(self, path="..\\data\\interim\\frame\\"):
        ocr_text = {}
        for index, id in enumerate(self.enable_data["IndexedID"]):
            dir_frame = path + id
            ocr_text[id] = self.__get_ocr_text(dir_frame)
            print(f"epoch: {index}/100")
        return ocr_text

    def __ocr_to_list(self, ocr_text: dict) -> list:
        return [value for value in ocr_text.values()]

    def __damp_ocr_text(self, ocr_text,
                        path="..\\data\\interim\\ocr_text.json"):
        with open(path, "w") as f:
            json.dump(ocr_text, f, indent=4)

    def tokenize(self, text_dict: dict,
                 except_pos=["BOS/EOS", "記号", "助詞"]) -> dict:
        mecab = MeCab.Tagger()  # defaul dictionary is ipadic-neologd here
        texts = {}
        for key, sentence in text_dict.items():
            tokenized = []
            node = mecab.parseToNode(sentence)
            while node:
                pos = node.feature.split(",")[0]
                if pos in except_pos:
                    node = node.next
                    continue
                else:
                    tokenized.append(node.surface)
                    node = node.next
            texts[key] = tokenized
        return texts

    def vectorize(self, word_dict, dim=300, return_except_words=False):
        vectors = {}
        except_word = []
        for key, words in word_dict.items():
            vector = np.zeros(dim)
            for word in words:
                try:
                    vector += self.model[word]
                except KeyError:
                    if word not in except_word:
                        except_word.append(word)
    #         vectors[key] = vector/len(words)  # 32100個の要素がnanになる
            vectors[key] = vector
        if return_except_words is True:
            return vectors, except_word
        else:
            return vectors

    def normalize(self, text):
        normalized_text = self.__normalize_unicode(text)
        normalized_text = self.__normalize_number(normalized_text)
        normalized_text = self.__lower_text(normalized_text)
        return normalized_text

    def __lower_text(self, text):
        return text.lower()

    def __normalize_unicode(self, text, form='NFKC'):
        unicode_normalized_text = unicodedata.normalize(form, text)
        return unicode_normalized_text

    def __normalize_number(self, text):
        # 連続した数字を0で置換
        replaced_text = re.sub(r'\d+', '0', text)
        return replaced_text

    def remove_stopwords(self, words):
        words = [word for word in words if word not in self.load.stopwords()]
        return words

    def damp(self, path="..\\data\\interim\\df.pkl"):
        self.enable_data.to_pickle(path)
