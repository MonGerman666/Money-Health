# crnn.py
import torch
import torch.nn as nn

class CRNN(nn.Module):
    def __init__(self, imgH, nc, nclass, nh):
        """
        imgH: altura de la imatge
        nc: nombre de canals (1 per escala de grisos)
        nclass: número total de caràcters (incloent un caràcter en blanc per a CTC)
        nh: mida de la capa oculta per l'RNN
        """
        super(CRNN, self).__init__()
        assert imgH % 16 == 0, "L'altura de la imatge ha de ser múltiple de 16"
        
        self.cnn = nn.Sequential(
            # Capa 1: (input: nc x imgH x imgW) -> (64 x imgH x imgW)
            nn.Conv2d(nc, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),
            
            # Capa 2
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),
            
            # Pots afegir més capes segons la complexitat...
        )
        
        # Després de les capes convolucionals, assumim que la sortida té dimensions: (batch, 128, H', W')
        # Ara, reordenem la sortida per passar-la per l'RNN. H' hauria de ser imgH / 4.
        self.rnn = nn.LSTM(128 * (imgH // 4), nh, num_layers=2, bidirectional=True)
        self.fc = nn.Linear(nh * 2, nclass)

    def forward(self, x):
        # x: (batch, nc, H, W)
        conv = self.cnn(x)  # (batch, 128, H', W')
        batch, channels, H, W = conv.size()
        # Permuta per tenir la dimensió de la seqüència en primer lloc
        conv = conv.permute(3, 0, 1, 2)  # (W, batch, channels, H)
        conv = conv.view(W, batch, channels * H)  # (W, batch, feature)
        recurrent, _ = self.rnn(conv)  # recurrent: (W, batch, nh*2)
        T, batch, hidden = recurrent.size()
        output = self.fc(recurrent.view(T * batch, hidden))
        output = output.view(T, batch, -1)
        return output
