import sys
import os
import re
import pprint
from itertools import takewhile, dropwhile

gtlds = ['edu', 'com', 'biz', 'info', 'net', 'org', 'xxx', 'gov', 'mil']
ctlds = ["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bm", "bn", "bo", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cs", "cu", "cv", "cx", "cy", "cz", "dd", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "No", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "yu", "za", "zm", "zw"]
used_ctlds = ["us", "uk"]
tld_bit = ('|').join(gtlds + used_ctlds)
dot = '(?:[\.;]|(?:\[|\(|\s|%20)\s*do?t\s*(?:\]|\)|\s|%20|&nbsp;)|\s+)'
at = '\s*(?:@|(?:\[|\(|\s|%20)\s*at\s*(?:\]|\)|\s|%20)|&#x40;|&#64;)\s*'
pat1 = '(?:&lt;)?(?:&gt;)?(?:(?:\w+\W)*e?mail:?(?:\s?to)?:?\s)?((?:\w+%(dot)s)*\w+)%(at)s((?:\w+%(dot)s)+(?:%(tld_bit)s))\\b(?!\s*Port 80)' % {"at": at, "dot": dot, "tld_bit": tld_bit}
pat3 = '>\s*((?:\w+\s)+(?:%s))\s*<' % tld_bit    
pat4 = '<script>[^<]*\(\'((?:\w+\.)+(?:%s))\',\'((?:\w+\.)*\w+)\'\)[^<]*</script>' % tld_bit
pat5 = '<script>[^<]*\(\'((?:\w+\.)*\w+)\',\'((?:\w+\.)+(?:%s))\'\)[^<]*</script>' % tld_bit
pat6 = '((?:\w+%(dot)s)*\w+)\W+f.*y\s*(?:&ldquo;|")%(at)s((?:\w+%(dot)s)+(?:%(tld_bit)s))' % {"at": at, "dot": dot, "tld_bit": tld_bit}
ph_pat1 = '\\b[\(\[]?([2-9]\d{2})[\)\]-]?\s{0,2}[\(\[]?([2-9]\d{2})[\)\]-]?\s{0,2}(\d{4})\\b'

""" 
TODO
This function takes in a filename along with the file object (actually
a StringIO object at submission time) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***, as it will be called directly by
the submit script

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO at submission time. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""

def first_match(line, res, name):
    matches = re.findall(pat1,line, re.IGNORECASE)
    for m in matches:
        str_list = filter(None, m)
        user = re.sub(dot, '.', str_list[0])
        domain = re.sub(dot, '.', str_list[1])
        email = '%s@%s' % (user, domain)
        # print m, line, email
        res.append((name,'e',email))
    

def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        first_match(line, res, name)
        for char in ['-', '_']:
            if re.findall('/w%s' % char, line) > 7:
                first_match(re.sub(char, '',line), res, name)
        matches = re.findall(pat3, line, re.IGNORECASE)
        for m in matches:
            str_list = re.split('\s+', m)
            if (len(str_list) %2 != 0):
                odd_parts = map(lambda i: str_list[i],filter(lambda i: i%2 == 0,range(len(str_list))))
                email = '%s@%s' % (odd_parts[0], '.'.join(odd_parts[1:]))
                res.append((name, 'e', email))
        for pattern in [pat4, pat5, pat6]:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for m in matches:
                order = (m[1], m[0]) if pattern == pat4 else (m[0], m[1])
                email = '%s@%s' % order
                res.append((name, 'e', email))
        
        matches = re.findall(ph_pat1, line)
        for m in matches:
            phone = '%s-%s-%s' % m
            res.append((name, 'p', phone))        
    return res

"""
You should not need to edit this function, nor should you alter
its interface as it will be called directly by the submit script
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
