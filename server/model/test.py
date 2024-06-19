import model.sa.sentiment as sentiment

sen = sentiment
sen.load('sentiment.marshal')
sen.train('./neg.txt', './pos.txt')
