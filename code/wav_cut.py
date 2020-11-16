import os
import json
import xml.etree.ElementTree as ET

from pydub import AudioSegment

AudioSegment.converter = "c:\\code\\ffmpeg"


def read_xml(path):
    tree = ET.ElementTree(file=path)
    res = []
    text = []
    try:
        for sbj in tree.iter(tag='subject'):
            if sbj.attrib['value'] != 'search':
                continue
            for elem in sbj.iter(tag='channel'):
                cur_channel = elem.attrib['no']
                for child in elem.iter(tag='items'):
                    start_end = []
                    duration_list = child.getchildren()
                    for item in duration_list:
                        start_end.append([item.attrib['start'], item.attrib['end']])
                    tmp = {cur_channel: start_end}
                    res.append(tmp)
                for cur_text, cur_time in zip(elem.iter(tag='text'), elem.iter(tag='time')):
                    text.append([cur_text.text, cur_time.text])
    except:
        print(path + " error")
        return [], []

    return res, text


def get_wav_slice(xml_file_path):
    wav_path = xml_file_path.replace("../data/xml/", "../data/wav/").replace(".xml", "")
    cur_wav_id = wav_path.replace("../data/wav/", "").replace(".wav", "") + "/"
    s_e_res_dict = []
    res_text = []
    try:
        s_e_res_dict, res_text = read_xml(xml_file_path)
        print(xml_file_path)
    except:
        print("Error: " + xml_file_path)
    if not s_e_res_dict:
        return

    target_path = "../data/processed_data/" + cur_wav_id
    if not os.path.exists(target_path):
        os.mkdir(target_path)

    text_path = target_path + "text_time.json"
    with open(text_path, "w+", encoding='utf-8') as f:
        json.dump(res_text, f, indent=1, ensure_ascii=False)

    cur_audio = AudioSegment.from_file(wav_path, format='wav')

    for d in s_e_res_dict:
        for character in d:
            character_path = target_path + str(character)
            if not os.path.exists(character_path):
                os.mkdir(character_path)
            for s_e_tuple in d[character]:
                cur_audio_path = character_path + "/" + str(s_e_tuple[0]) + "_" + str(s_e_tuple[1]) + ".wav"
                chunk_data = cur_audio[int(s_e_tuple[0]):int(s_e_tuple[1])]
                chunk_data.export(cur_audio_path, format="wav")


if __name__ == '__main__':
    xml_path = "../data/xml/"
    for root, dirs, files in os.walk(xml_path):
        for file in files:
            get_wav_slice(xml_path + file)
