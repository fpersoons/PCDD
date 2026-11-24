frag=open('dist/guide.html',encoding='utf8').read()
pre=('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
 '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
 '<meta name="author" content="Chemonics International — projet GHSC-PSM">\n'
 '<meta name="description" content="Guide développeur du PCDD — novembre 2026.">\n'
 '<style>:root{color-scheme:light dark}html,body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n\n')
i=frag.rindex('</style>')+len('</style>')
out=pre+frag[:i]+'\n\n</head>\n<body>'+frag[i:]+'\n\n</body>\n</html>\n'
open('dist/Guide_developpeur_PCDD.html','w',encoding='utf8').write(out)
print('HTML autonome :',len(out)//1024,'Ko')

import shutil
shutil.copyfile('dist/guide.docx', 'dist/Guide_developpeur_PCDD.docx')
print('DOCX livrable : dist/Guide_developpeur_PCDD.docx')
