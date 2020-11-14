import os
import xml.etree.ElementTree as ET

from pydub import AudioSegment


AudioSegment.converter = "c:\\code\\ffmpeg"


def read_xml(path):
    tree = ET.ElementTree(file=path)
    res = []
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

    return res


def get_wav_slice(xml_file_path):
    wav_path = xml_file_path.replace("../data/xml/", "../data/wav/").replace(".xml", "")
    cur_wav_id = wav_path.replace("../data/wav/", "").replace(".wav", "") + "/"
    s_e_res_dict = read_xml(xml_file_path)

    target_path = "../data/processed_data/" + cur_wav_id
    if not os.path.exists(target_path):
        os.mkdir(target_path)

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
