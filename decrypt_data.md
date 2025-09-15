```sh
tar -cvzf - folder | gpg -c --passphrase yourpassword > folder.tar.gz.gpg
gpg -d folder.tar.gz.gpg | tar -xvzf -
```
hint=I5ath
