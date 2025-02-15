textMessage = 'Hello World.';

% 1. Знаковое кодирование
encodedBits = symbolEncoder(textMessage);
% disp('Encoded Bits (Symbol Encoder):');
% disp(encodedBits);

% 2. Сверточное кодирование
convEncodedBits = convolutionalEncoder(encodedBits);
% disp('Convolutionally Encoded Bits:');
% disp(convEncodedBits);

% 3. Декодирование Витерби
decodedBits = viterbiDecoder(convEncodedBits);
% disp('Decoded Bits (Viterbi Decoder):');
% disp(decodedBits);

% 4. Знаковое декодирование
decodedMessage = symbolDecoder(decodedBits);
% disp('Decoded Message:');
% disp(decodedMessage);

if isequal(textMessage, decodedMessage)
    disp('Test PASSED: Message decoded successfully.');
else
    disp('Test FAILED: Decoded message does not match original.');
    disp(['Original Message:  ', textMessage]);
    disp(['Decoded Message:   ', decodedMessage]);
end