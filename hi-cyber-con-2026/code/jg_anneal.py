#!/usr/bin/env python3
import random, math, re
tokens = "53 74 u3 17 35 x3 x2 76 24 33 93 u3 16 v4 36 v4 93 32 64 22 z3 x2 42 w4 54 05 v2 v5 63 v6 26 23 26 33 86 u3 33 x3 74 x2 06 54 62 x5 22 74 44 04 45 v5 93 x2".split()
syms = sorted(set(tokens))
S = len(syms)
symidx = {s:i for i,s in enumerate(syms)}
seq = [symidx[t] for t in tokens]

# English letter log-frequencies
LF = {'a':8.17,'b':1.49,'c':2.78,'d':4.25,'e':12.70,'f':2.23,'g':2.02,'h':6.09,'i':6.97,'j':0.15,
'k':0.77,'l':4.03,'m':2.41,'n':6.75,'o':7.51,'p':1.93,'q':0.10,'r':5.99,'s':6.33,'t':9.06,'u':2.76,
'v':0.98,'w':2.36,'x':0.15,'y':1.97,'z':0.07,' ':13.0,'{':0.4,'}':0.4,'_':1.0,'0':0.5,'1':0.4,'2':0.3,'3':0.2,'4':0.2,'5':0.2,'6':0.2,'7':0.2,'8':0.2,'9':0.2}
LF = {k: math.log(v/100.0) for k,v in LF.items()}
# top quadgrams (approx log probs)
QUAD = {'tion':-5.5,'nthe':-5.8,'ther':-5.9,'that':-6.0,'ofth':-6.0,'fthe':-6.0,'with':-6.2,'inth':-6.3,'atio':-6.3,
'othe':-6.3,'tthe':-6.3,'dthe':-6.5,'ethe':-6.5,'sand':-6.6,'ment':-6.6,'this':-6.6,'ingt':-6.7,'hing':-6.7,
'here':-6.8,'from':-6.9,'ough':-6.9,'were':-7.0,'the':-4.5,'and':-4.8,'ing':-5.0,'you':-6.5,'flag':-7.5,'hictf':-8.0,'note':-7.0,'noon':-7.5,'saad':-8.5,'harun':-8.5}
WORDS = ['the','and','this','that','with','from','flag','note','code','noon','meet','building','watching','saad','harun','hictf','you','your','will','at','is','it','say','says','said']

def score(dec):
    s = 0.0
    # letter freq
    for ch in dec: s += LF.get(ch, -12.0)
    # quadgrams
    d = dec.lower()
    for i in range(len(d)-3):
        g = d[i:i+4]
        if g in QUAD: s += QUAD[g]*2.0
    # words
    for w in WORDS:
        c = d.count(w)
        s += c * (6.0 if len(w)>3 else 3.0)
    if 'hictf{' in d: s += 120.0
    if d.count('{') and d.count('}') and d.index('{')<d.rindex('}'): s += 15.0
    # penalty weird
    for ch in d:
        if ch not in LF: s -= 6.0
    return s

best_global = -1e18
best_map = None
random.seed(1337)
for restart in range(40):
    mp = list(range(S))
    random.shuffle(mp)
    inv = [0]*S
    for i,v in enumerate(mp): inv[v]=i
    cur = [chr(97+i) if i<26 else '{' for i in range(40)]  # placeholder
    # map symbol -> char from a pool
    pool = list('etaoinshrdlucmfwypvbgkqjxz{}_0123456789')
    # assign each symbol a char
    assign = [random.choice(pool) for _ in range(S)]
    def dec_of(assign):
        return ''.join(assign[s] for s in seq)
    cur_score = score(dec_of(assign))
    T = 20.0
    for it in range(6000):
        i = random.randrange(S)
        old = assign[i]
        assign[i] = random.choice(pool)
        ns = score(dec_of(assign))
        d = ns - cur_score
        if d >= 0 or random.random() < math.exp(d / T):
            cur_score = ns
        else:
            assign[i] = old
        T *= 0.999
    if cur_score > best_global:
        best_global = cur_score
        best_map = assign[:]
        print(f"restart {restart}: score={cur_score:.1f}  {dec_of(assign)}", flush=True)
print("BEST:", best_global)
print(''.join(best_map[s] for s in seq))
