import os
# Print imediato para provar que o script começou
print("--- INICIANDO SCRIPT DE ATUALIZAÇÃO ---", flush=True)

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    print("Importações realizadas com sucesso.", flush=True)
except ImportError as e:
    print(f"ERRO CRÍTICO NAS IMPORTAÇÕES: {e}", flush=True)
    exit(1)

def get_service():
    print("Tentando autenticar...", flush=True)
    try:
        creds = Credentials(
            None,
            refresh_token=os.environ.get("REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET")
        )
        service = build("youtube", "v3", credentials=creds)
        print("Autenticação criada (Service Build OK).", flush=True)
        return service
    except Exception as e:
        print(f"ERRO NA AUTENTICAÇÃO: {e}", flush=True)
        raise e

def update_video():
    video_id = os.environ.get("VIDEO_ID")
    if not video_id:
        print("ERRO: VIDEO_ID não encontrado nas variáveis de ambiente.", flush=True)
        return

    print(f"Alvo: Vídeo ID {video_id} (Verificando...)", flush=True)
    
    youtube = get_service()

    try:
        # 1. Ler dados atuais
        print("Requisitando dados do vídeo na API...", flush=True)
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        if not response["items"]:
            print(f"ERRO FATAL: Vídeo com ID '{video_id}' não encontrado. Verifique se o ID está correto.", flush=True)
            return

        item = response["items"][0]
        likes = item["statistics"].get("likeCount", "0")
        current_title = item["snippet"]["title"]
        
        print(f"Status Atual -> Título: '{current_title}' | Likes: {likes}", flush=True)
        
        # 2. Definir novo título
        new_title = f"Este vídeo tem {likes} likes" 
        
        # Verifica se mudou
        if current_title == new_title:
            print(f"DECISÃO: Título já está correto. Nenhuma ação necessária.", flush=True)
            return

        # 3. Atualizar
        print(f"AÇÃO: Atualizando título para: '{new_title}'...", flush=True)
        item["snippet"]["title"] = new_title
        
        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": {
                    "title": new_title,
                    "categoryId": item["snippet"]["categoryId"],
                    "description": item["snippet"]["description"],
                    "tags": item["snippet"].get("tags", [])
                }
            }
        ).execute()
        
        print(f"SUCESSO TOTAL! Título atualizado.", flush=True)

    except HttpError as e:
        print(f"ERRO NA API DO GOOGLE: {e}", flush=True)
        # Tenta imprimir o conteúdo do erro para ajudar no debug
        if hasattr(e, 'content'):
            print(f"Detalhes do erro: {e.content}", flush=True)
    except Exception as e:
        print(f"ERRO GENÉRICO: {e}", flush=True)

if __name__ == "__main__":
    update_video()
    print("--- FIM DO SCRIPT ---", flush=True)
