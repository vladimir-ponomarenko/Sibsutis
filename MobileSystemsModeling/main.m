textMessage = 'Hello World.';

encodedBits = symbolEncoder(textMessage);
disp('Encoded Bits:');
disp(encodedBits);

decodedMessage = symbolDecoder(encodedBits);
disp('Decoded Message:');
disp(decodedMessage);