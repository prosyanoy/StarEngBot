import audioread
import librosa
import webrtcvad
import numpy as np
import subprocess
import io
import soundfile as sf

def load_and_trim(file_path, sr=16000, top_db=20):
    """
    Универсальная загрузка .ogg/.wav c авто-конвертацией:
    * сначала пробуем librosa → soundfile/FFmpeg
    * если soundfile не умеет Ogg, используем ffmpeg → stdout
    """
    try:
        y, sr_out = librosa.load(str(file_path), sr=sr)
    except (RuntimeError, sf.LibsndfileError, audioread.NoBackendError):
        # ¬ fallback через ffmpeg
        cmd = [
            "ffmpeg", "-v", "quiet", "-i", str(file_path),
            "-ar", str(sr), "-ac", "1", "-f", "wav", "-"
        ]
        wav_bytes = subprocess.check_output(cmd)          # FFmpeg ⟶ stdout
        y, sr_out = sf.read(io.BytesIO(wav_bytes), dtype="float32")
    # обрезаем тишину, если нужно
    y_trim, _ = librosa.effects.trim(y, top_db=top_db)
    return y_trim, sr_out

def extract_mfcc(y, sr, n_mfcc=13):
    # Вычисление MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Можно добавить дельты и дельта-дельты:
    delta = librosa.feature.delta(mfcc, mode='nearest')
    delta2 = librosa.feature.delta(mfcc, order=2, mode='nearest')
    features = np.vstack([mfcc, delta, delta2])
    return features

def compute_dtw(features_ref, features_test):
    # Расчет DTW с использованием евклидовой метрики
    D, wp = librosa.sequence.dtw(X=features_ref, Y=features_test, metric='euclidean')
    dtw_cost = D[-1, -1]
    # Нормализация стоимости по длине оптимального пути
    norm_cost = dtw_cost / len(wp)
    return norm_cost, wp

def convert_to_pcm16(y):
    """
    Преобразует float-аудио ([-1, 1]) в байты PCM16 (little-endian).
    """
    # Масштабируем до диапазона int16 и конвертируем
    y_int16 = np.int16(y * 32767)
    return y_int16.tobytes()

def frame_generator(frame_duration_ms, audio_bytes, sample_rate):
    """
    Разбивает аудио (в виде байтов PCM16) на фреймы длительностью frame_duration_ms.
    """
    frame_size = int(sample_rate * frame_duration_ms / 1000)  # число сэмплов в фрейме
    n_bytes = frame_size * 2  # 2 байта на сэмпл для PCM16
    offset = 0
    frames = []
    while offset + n_bytes <= len(audio_bytes):
        frames.append(audio_bytes[offset:offset+n_bytes])
        offset += n_bytes
    return frames

def analyze_vad(y, sr, frame_duration_ms=30, vad_mode=3):
    """
    Анализирует аудио на наличие речи по фреймам с использованием webrtcvad.
    Возвращает список булевых значений: True, если в фрейме обнаружена речь.
    """
    vad = webrtcvad.Vad(vad_mode)  # режим 3 - максимально агрессивный
    audio_bytes = convert_to_pcm16(y)
    frames = frame_generator(frame_duration_ms, audio_bytes, sr)
    speech_flags = [vad.is_speech(frame, sr) for frame in frames]
    return speech_flags, frames


def analyse(file_path):
    y, sr = load_and_trim(file_path)

    # Анализируем аудио: получаем для каждого фрейма, есть ли речь
    speech_flags, frames = analyze_vad(y, sr, frame_duration_ms=30, vad_mode=3)

    # Выводим количество речевых и неречевых фреймов
    num_frames = len(speech_flags)
    num_speech = sum(speech_flags)
    # print(f"Всего фреймов: {num_frames}, речевых: {num_speech}, неречевых: {num_frames - num_speech}")

    # Если необходимо, можно собрать аудио только с речевыми фреймами:
    speech_audio_bytes = b"".join([frame for flag, frame in zip(speech_flags, frames) if flag])
    # Для дальнейшей обработки можно преобразовать обратно в numpy массив:
    speech_audio = np.frombuffer(speech_audio_bytes, dtype=np.int16).astype(np.float32) / 32767.

    return extract_mfcc(speech_audio, sr)