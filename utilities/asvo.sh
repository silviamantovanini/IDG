#! /bin/bash -l
#SBATCH --export=ALL,MWA_ASVO_API_KEY,SINGULARITY_BINDPATH
#SBATCH --mem=200GB
#SBATCH --time=05:00:00
#SBATCH --output=asvo.o%A
#SBATCH --error=asvo.e%A

wget "https://projects.pawsey.org.au/mwa-asvo/1086451000_798020_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=ON1Vh2bu8BArzMMcXfNag0h6sEc%3D&Expires=1729615205" -O 1086451000_798020_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1086451600_798021_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=RTwUxljbj1Ky0%2FOZGJqmsWtPTgA%3D&Expires=1729587194" -O 1086451600_798021_ms.tar 
wget "https://projects.pawsey.org.au/mwa-asvo/1091271960_798022_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=7GjwvkjLRruVjhb7juB9oBi2sOI%3D&Expires=1729615611" -O 1091271960_798022_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1111692624_798023_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=R%2FbkPs9l36jAUnE9ny2VlLPRDk8%3D&Expires=1729614619" -O 1111692624_798023_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1111693224_798024_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=%2BARUzxnSQRr%2BZzMUcMwX50f%2B2DU%3D&Expires=1729616651" -O 1111693224_798024_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1114880664_798025_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=SXQuO3kc2R8SyszgPzaC8oK%2BWH8%3D&Expires=1729616715" -O 1114880664_798025_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1114881264_798026_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=pCNAFR1fPjsmwZ81M5BE%2BXWvmkE%3D&Expires=1729616950" -O 1114881264_798026_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1119800688_798027_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=UspKhDYpSt0JgCRj39CsVri%2FsYE%3D&Expires=1729616984" -O 1119800688_798027_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1119801288_798028_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=ExL5aAJljKcDG4kHVbOacE%2F%2Fesw%3D&Expires=1729617253" -O 1119801288_798028_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1122894184_798029_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=OY1K%2FJHoLz%2FwiCaSRXJZJ23vIjw%3D&Expires=1729617500" -O 1122894184_798029_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1204836344_798030_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=nl6jtZlizzLvkBKOlHET%2F5ZtTJM%3D&Expires=1729618661" -O 1204836344_798030_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1209665744_798031_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=ZvOA7SktcK5Hh0jcZ1WFucR7slw%3D&Expires=1729619112" -O 1209665744_798031_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210264392_798032_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=7tMxS5ngLIWPq%2B38NYJBrFDgPkQ%3D&Expires=1729619188" -O 1210264392_798032_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210264992_798033_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=ahFLESFRccuX%2FZazQkU8pQKd2vM%3D&Expires=1729619901" -O 1210264992_798033_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210875944_798034_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=KDZMoaQE4Fw8Xb9SU0nhYaxqhpQ%3D&Expires=1729620252" -O 1210875944_798034_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210876544_798035_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=De9qyHSwDoJk6f4ERhMyJCXwfr4%3D&Expires=1729620257" -O 1210876544_798035_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1211647520_798036_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=b%2FrZU9W4asZJh5cxolFvgWJADUI%3D&Expires=1729621097" -O 1211647520_798036_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1213280136_798037_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=XGyQekvh6MdYtdHgBmg596cRQWE%3D&Expires=1729621397" -O 1213280136_798037_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1213280736_798038_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=Jn2a%2B2euZoE0C%2BKy%2Bcevdpq%2FR3g%3D&Expires=1729621431" -O 1213280736_798038_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1243183576_798039_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=gpqSTqcBC5O0IGzNmugdSgLofBM%3D&Expires=1729622126" -O 1243183576_798039_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1244816192_798040_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=4insdcxwt1lTC2xgzLeKhbmtw78%3D&Expires=1729622333" -O 1244816192_798040_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1244816792_798041_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=piJi%2BIPg0gNwGE%2F9m5I6PZ9FPXo%3D&Expires=1729622464" -O 1244816792_798041_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1086457000_798042_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=5e3vuAyAvEAFUWOSxBEOLhPuzRU%3D&Expires=1729589425" -O 1086457000_798042_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1091269560_798043_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=j57jnTt3xwhYzKC9oD1klyTermM%3D&Expires=1729622365" -O 1091269560_798043_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1111693824_798044_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=LPNiSZIEZrJp59pwKVfPI%2BNlhdE%3D&Expires=1729589656" -O 1111693824_798044_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1114869264_798045_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=53MBjnM%2BD8MzXSg%2BawnoFO6teGc%3D&Expires=1729622767" -O 1114869264_798045_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1119792288_798046_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=V4SyjXP1Oh2bx57VHkEmcooev%2BQ%3D&Expires=1729622730" -O 1119792288_798046_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1122891784_798047_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=au1PQsP43kcSWzcbbKvfcckX%2Bkk%3D&Expires=1729623042" -O 1122891784_798047_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1204816848_798048_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=6KEDbpKf3n1uEG%2BEcRzRWdeZ8WA%3D&Expires=1729624051" -O 1204816848_798048_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1209651344_798049_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=qZc%2BTKk2vE%2Bdgi0jaipoAag5ePo%3D&Expires=1729624587" -O 1209651344_798049_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210255392_798050_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=gChJFJNa1%2FxrPnc5hz7QLoHKE7E%3D&Expires=1729624897" -O 1210255392_798050_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1210881944_798051_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=%2BazKxp57E0G4vLY96r6l73hT9Kg%3D&Expires=1729592421" -O 1210881944_798051_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1211633120_798052_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=1CQ5PYXaBkgjaXHWsWh5zGpzdWY%3D&Expires=1729625856" -O 1211633120_798052_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1213271136_798053_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=qmRU1R0jOOJF8%2Bu0HQhgMMApwt8%3D&Expires=1729625859" -O 1213271136_798053_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1243169176_798054_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=uBdd1hbU%2Fqei57EZE1UDKiWzd28%3D&Expires=1729626096" -O 1243169176_798054_ms.tar
wget "https://projects.pawsey.org.au/mwa-asvo/1244807192_798055_ms.tar?AWSAccessKeyId=a5e466f891734d45a67676504a309c35&Signature=f3yYfSrtCrMNcevGTOzfS8ck%2Fg0%3D&Expires=1729626680" -O 1244807192_798055_ms.tar

for file in *tar
do
        srun tar -xvf $file
	rm $file
done
