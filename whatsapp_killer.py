import os
import time
import random
import subprocess
import threading
import psutil
import sys

# Configurações
TARGET_APP = "com.whatsapp"
DURATION_MINUTES = 5
CPU_STRESSORS = 4

def find_whatsapp_pid():
    """Encontra o PID do WhatsApp no Android."""
    try:
        # Tenta usar adb para encontrar o PID
        output = subprocess.check_output(['adb', 'shell', 'pidof', TARGET_APP], stderr=subprocess.STDOUT).decode().strip()
        pids = output.split()
        return [int(pid) for pid in pids if pid.isdigit()]
    except Exception as e:
        print(f"[WARN] ADB não encontrado ou erro: {e}")
        return []

def cpu_stressor():
    """Gera carga de CPU no sistema."""
    def burn_cpu():
        while True:
            _ = [x * x for x in range(10**6)]
    
    threads = []
    for _ in range(CPU_STRESSORS):
        t = threading.Thread(target=burn_cpu, daemon=True)
        t.start()
        threads.append(t)
    return threads

def memory_stressor(size_mb):
    """Aloca memória para causar pressão no sistema."""
    print(f"[MEM] Alocando {size_mb}MB...")
    chunks = []
    target_bytes = size_mb * (1024**2)
    chunk_size = 1024**2 * 10 # 10MB
    
    while sum(len(c) for c in chunks) < target_bytes:
        chunks.append(b'\x00' * chunk_size)
    return chunks

def io_stressor(size_mb):
    """Satura o disco com writes."""
    filename = f"chaos_{os.getpid()}.tmp"
    print(f"[IO] Iniciando saturação de disco ({size_mb}MB)...")
    with open(filename, 'wb') as f:
        chunk = b'\x00' * (1024 * 1024) # 1MB
        for _ in range(size_mb):
            f.write(chunk)
    os.remove(filename)

def manipulate_whatsapp_priority(pids):
    """Tenta mudar a prioridade do WhatsApp para 'Baixa'."""
    for pid in pids:
        try:
            # No Linux/Android, nice 19 é a prior