import matplotlib.pyplot as plt
import numpy as np
import random

def string_to_bits(s):
    result = []
    for char in s:
        bits = bin(ord(char))[2:].zfill(8)
        result.extend([int(bit) for bit in bits])
    return result

def visualize_bits(bits, title="Bit Visualization"):
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.step(range(len(bits)), bits, where='post')
    
    min_val = min(bits)
    max_val = max(bits)
    if min_val != max_val:
        ax.set_ylim([min_val - 0.5, max_val + 0.5])
    
    ax.set_xlabel("Bit Index")
    ax.set_ylabel("Bit Value")
    ax.set_title(title)
    ax.grid(True)
    plt.show()

def calculate_crc(data, generator):
    data_size = len(data)
    generator_size = len(generator)
    extended_data = data + [0] * (generator_size - 1)

    for i in range(data_size):
        if extended_data[i] == 1:
            for j in range(generator_size):
                extended_data[i + j] ^= generator[j]

    crc = extended_data[data_size:]
    return crc

def generate_gold_sequence(reg1_init, reg2_init, seq_length):
    reg1 = reg1_init[:]
    reg2 = reg2_init[:]
    gold_sequence = []

    for _ in range(seq_length):
        out_reg1 = reg1[4]
        out_reg2 = reg2[4]

        feedback1 = reg1[1] ^ reg1[4]
        reg1 = [feedback1] + reg1[:-1]

        feedback2 = reg2[0] ^ reg2[1] ^ reg2[2]
        reg2 = [feedback2] + reg2[:-1]

        gold_sequence.append(out_reg1 ^ out_reg2)

    return gold_sequence

def bits_to_time_samples(bits, samples_per_bit):
    time_samples = []
    for bit in bits:
        time_samples.extend([bit] * samples_per_bit)
    return time_samples

def correlate(signal, pattern):
    signal_np = np.array(signal)
    pattern_np = np.array(pattern)
    correlation = np.correlate(signal_np, pattern_np, mode='valid')
    return correlation / (np.linalg.norm(signal_np) * np.linalg.norm(pattern_np))

def decode_time_samples(time_samples, samples_per_bit, threshold):
    decoded_bits = []
    for i in range(0, len(time_samples) - (len(time_samples) % samples_per_bit), samples_per_bit):
        chunk = time_samples[i:i + samples_per_bit]
        mean_value = np.mean(chunk)
        decoded_bits.append(1 if mean_value > threshold else 0)
    return decoded_bits

def check_errors(data, generator):
    calculated_crc = calculate_crc(data, generator)
    return all(bit == 0 for bit in calculated_crc)

def bits_to_string(bits):
    string = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        char_code = int("".join(str(bit) for bit in byte), 2)
        string += chr(char_code)
    return string

def visualize_spectrum(signal, fs, title="Signal Spectrum"):
    frequencies = np.fft.fftfreq(len(signal), 1/fs)
    spectrum = np.abs(np.fft.fft(signal))
    
    plt.figure(figsize=(10, 4))
    plt.plot(frequencies, spectrum)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title(title)
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    name = input("Enter your first name (latin letters): ")
    surname = input("Enter your last name (latin letters): ")

    full_name = name + surname

    bit_sequence = string_to_bits(full_name)

    print("Bit sequence:", bit_sequence)
    visualize_bits(bit_sequence, "Bit Sequence")

    print("\nASCII Coder:")
    for char in full_name:
        ascii_code = ord(char)
        binary_representation = bin(ascii_code)[2:].zfill(8)
        print(f"'{char}': {ascii_code} (decimal), {binary_representation} (binary)")

    generator = [1, 0, 1, 1, 1, 0, 1, 1]
    crc = calculate_crc(bit_sequence, generator)

    print("\nCRC Generator:", generator)
    print("Calculated CRC:", crc)

    bit_sequence_with_crc = bit_sequence + crc

    reg1_init = [1, 0, 1, 0, 1]
    reg2_init = [1, 1, 1, 0, 1]
    gold_sequence_length = 31  # G
    gold_sequence = generate_gold_sequence(reg1_init, reg2_init, gold_sequence_length)

    print("\nGold Sequence:", gold_sequence)

    final_bit_sequence = gold_sequence + bit_sequence_with_crc

    print("\nFinal bit sequence (Gold + Data + CRC):", final_bit_sequence)
    visualize_bits(final_bit_sequence, "Final Bit Sequence (Gold + Data + CRC)")

    fs = 100
    samples_per_bit_values = [5, 10, 20]

    spectra = []
    noisy_spectra = []

    for samples_per_bit in samples_per_bit_values:
        time_samples = bits_to_time_samples(final_bit_sequence, samples_per_bit)
        
        print(f"\nTime samples (N={samples_per_bit}):", time_samples)
        visualize_bits(time_samples, f"Time Samples (Amplitude Modulation, N={samples_per_bit})")

        visualize_spectrum(time_samples, fs, f"Transmitted Signal Spectrum (N={samples_per_bit})")

        L = len(bit_sequence)
        M = len(crc)
        G = gold_sequence_length
        N = samples_per_bit

        signal_length = 2 * N * (L + M + G)
        signal = [0] * signal_length

        while True:
            try:
                shift_str = input(f"Enter shift from 0 to {N * (L + M + G)} (N={samples_per_bit}): ")
                shift = int(shift_str)
                if 0 <= shift <= N * (L + M + G):
                    break
                else:
                    print("Shift value must be within the specified range.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        signal[shift : min(shift + len(time_samples), signal_length)] = time_samples[:min(len(time_samples), signal_length - shift)]

        print("Signal:", signal)
        visualize_bits(signal, f"Signal with Shift (N = {samples_per_bit})")

        sigma = float(input(f"Enter sigma for noise (float, N={samples_per_bit}): "))
        noise = np.random.normal(0, sigma, signal_length)

        noisy_signal = (np.array(signal) + noise).tolist()

        visualize_bits(noisy_signal, f"Noisy Signal (N={samples_per_bit})")

        visualize_spectrum(noisy_signal, fs, f"Noisy Signal Spectrum (N={samples_per_bit})")

        frequencies = np.fft.fftfreq(len(signal), 1/fs)
        spectrum = np.abs(np.fft.fft(signal))
        
        frequencies_noisy = np.fft.fftfreq(len(noisy_signal), 1/fs)
        spectrum_noisy = np.abs(np.fft.fft(noisy_signal))
        
        spectra.append((frequencies, spectrum, f"Signal, N={samples_per_bit}"))
        noisy_spectra.append((frequencies_noisy, spectrum_noisy, f"Noisy, N={samples_per_bit}"))

        gold_time_samples = bits_to_time_samples(gold_sequence, samples_per_bit)
        correlation_result = correlate(noisy_signal, gold_time_samples)

        start_index = np.argmax(correlation_result)

        print(f"Gold sequence starts at index: {start_index}")

        received_data_samples = noisy_signal[start_index:]

        visualize_bits(received_data_samples, f"Received Data Samples (After Correlation, N={samples_per_bit})")

        threshold = 0.5
        decoded_bits = decode_time_samples(received_data_samples, samples_per_bit, threshold)

        print(f"Decoded bits (with Gold and CRC, N = {samples_per_bit}): {decoded_bits}")
        visualize_bits(decoded_bits, f"Decoded Bits (with Gold and CRC, N= {samples_per_bit})")

        decoded_bits_without_gold = decoded_bits[gold_sequence_length:]

        print(f"Decoded bits (without Gold, with CRC, N= {samples_per_bit}): {decoded_bits_without_gold}")
        visualize_bits(decoded_bits_without_gold, f"Decoded Bits (without Gold, with CRC, N={samples_per_bit})")

        if check_errors(decoded_bits_without_gold[:-len(crc)], generator):
            print("No errors detected!")
            decoded_data_bits = decoded_bits_without_gold[:-len(crc)]
            decoded_string = bits_to_string(decoded_data_bits)
            print("Decoded string:", decoded_string)
        else:
            print("Errors detected!")

    plt.figure(figsize=(12, 6))
    
    for freq, spec, label in spectra:
        plt.plot(freq, spec, label=label)
    
    for freq, spec, label in noisy_spectra:
        plt.plot(freq, spec, linestyle='--', label=label)
    
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("Signal Spectrums for Different N Values")
    plt.legend()
    plt.grid(True)
    plt.show()
