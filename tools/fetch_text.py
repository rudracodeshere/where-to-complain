import sys,re,html,subprocess
u=sys.argv[1]
t=subprocess.run(['curl','-sL','-m','60','-A','Mozilla/5.0',u],capture_output=True).stdout.decode('utf8','ignore')
t=re.sub(r'(?s)<(script|style).*?</\1>','',t)
t=re.sub(r'(?i)<(br|/p|/div|/li|/tr|/h\d)[^>]*>','\n',t)
t=re.sub(r'<a [^>]*href="([^"]*)"[^>]*>',r' [LINK:\1] ',t)
t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t)
t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
print(t)
