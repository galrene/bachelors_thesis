## David
byteIndex = 0

byteIndexShifted   =   InvShiftRows [ byteIndex ]
st10Byte           =   ciphertext [ byteIndexShifted ]

byte        =   ciphertext [ byteIndex ] ^ key  # key is key byte?
st9Byte     =   InvSubBytes [ byte ]

hammDist ( st10Byte, st9Byte )

`!Davidov InvShiftRows robi to iste co ShiftRowIndex!`


## Metrisca

byteIndex = 0

byteIndexShifted    = ShiftRowIndex ( byteIndex )   # where curr B was after shift rows
st10Byte            = ciphertext [ byteIndexShifted ]

byte    = ciphertext [ byteIndex ] ^ key  # key is int from 0 to 256
st9Byte = InvSubBytes ( byte )

hammDist ( st10Byte, st9Byte )

---

## Notes

Zistia index po ShiftRows a ten byte v CT prehlasia za
byte stavoveho registra pred 10. rundou.

Pridaju kluc k CT na realnom indexe (bez ShiftRows) a reverznu na nom SBox.
Toto prehlasia za byte stavoveho registra pred 9. rundou (?).

Hladaju ich hammingovu vzdialenost.
