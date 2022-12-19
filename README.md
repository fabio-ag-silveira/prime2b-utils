# prime2b-utils
Scripts python para organização de arquivos.

Forma de usar: 

- zip_uploads.py

   ```shell
    python zip_uploads.py -d -z -i "path/to/input_dir" -o "path/to/output_dir"
    ```
    
    Onde:
    
    **-i**: Diretorio onde se encontra todos os sites (geralmente a pasta 'www' do servidor). 
    
    **-o**: Diretorio onde os arquivos .zip da pasta 'uploads' serao salvos.
    
    **-d**: Deleta arquivos suspeitos.
    
    **-z**: Compacta a pasta 'uploads'.
    
