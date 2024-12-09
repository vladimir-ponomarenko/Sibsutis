import matplotlib.pyplot as plt
import numpy as np
import random

def string_to_bits(s):
    result = []
    for char in s:
        bits = bin(ord(char))[2:].zfill(8)
        result.extend([int(bit) for bit in bits])
    return result

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
    return [bit for bit in bits for _ in range(samples_per_bit)]

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


def calculate_ber(original_bits, decoded_bits):
    errors = sum(1 for a, b in zip(original_bits, decoded_bits) if a != b)
    return errors / len(original_bits) if original_bits else 0


if __name__ == "__main__":
    name = input("Enter your first name (latin letters): ")
    surname = input("Enter your last name (latin letters): ")

    full_name = name + surname
    bit_sequence = string_to_bits(full_name)

    generator = [1, 0, 1, 1, 1, 0, 1, 1]
    crc = calculate_crc(bit_sequence, generator)
    bit_sequence_with_crc = bit_sequence + crc

    reg1_init = [1, 0, 1, 0, 1]
    reg2_init = [1, 1, 1, 0, 1]
    gold_sequence_length = 31
    gold_sequence = generate_gold_sequence(reg1_init, reg2_init, gold_sequence_length)
    final_bit_sequence = gold_sequence + bit_sequence_with_crc

    fs = 100

    samples_per_bit_values = range(1, 15)
    sigma_values = [0.1, 0.5, 1.0]
    plt.figure()

    for sigma in sigma_values:
        ber_vs_spb = []
        for spb in samples_per_bit_values:
            time_samples = bits_to_time_samples(final_bit_sequence, spb)
            noise = np.random.normal(0, sigma, len(time_samples))
            noisy_signal = (np.array(time_samples) + noise).tolist()
            decoded_bits = decode_time_samples(noisy_signal, spb, 0.5)
            ber = calculate_ber(final_bit_sequence, decoded_bits)
            ber_vs_spb.append(ber)
        plt.plot(samples_per_bit_values, ber_vs_spb, label=f"Sigma = {sigma}")


    plt.xlabel("Samples per bit")
    plt.ylabel("Bit Error Rate")
    plt.title("BER vs Samples per bit")
    plt.legend()
    plt.grid(True)
    plt.show()

    spb = 10
    sigma_values = np.linspace(0, 2, 20)
    ber_vs_sigma = []
    for sigma in sigma_values:
        time_samples = bits_to_time_samples(final_bit_sequence, spb)
        noise = np.random.normal(0, sigma, len(time_samples))
        noisy_signal = (np.array(time_samples) + noise).tolist()
        decoded_bits = decode_time_samples(noisy_signal, spb, 0.5)
        ber = calculate_ber(final_bit_sequence, decoded_bits)
        ber_vs_sigma.append(ber)

    plt.plot(sigma_values, ber_vs_sigma)
    plt.xlabel("Sigma (Noise Level)")
    plt.ylabel("Bit Error Rate")
    plt.title("BER vs Sigma")
    plt.grid(True)
    plt.show()


    spb = 10
    sigma_values = [0.1, 0.5, 1.0]
    threshold_values = np.linspace(0, 1, 20)
    plt.figure()

    for sigma in sigma_values:
        ber_vs_threshold = []
        for threshold in threshold_values:
            time_samples = bits_to_time_samples(final_bit_sequence, spb)
            noise = np.random.normal(0, sigma, len(time_samples))
            noisy_signal = (np.array(time_samples) + noise).tolist()
            decoded_bits = decode_time_samples(noisy_signal, spb, threshold)
            ber = calculate_ber(final_bit_sequence, decoded_bits)
            ber_vs_threshold.append(ber)

        plt.plot(threshold_values, ber_vs_threshold, label=f"Sigma = {sigma}")

    plt.xlabel("Correlation")
    plt.ylabel("Bit Error Rate")
    plt.title("BER vs Correlation")
    plt.legend()
    plt.grid(True)
    plt.show()
