# デプロイメモ

## docker

環境変数をセットアップします。

```bash
gcp_project=プロジェクトID
image_name=gemini-stg
```

プロジェクトを認証します。

```bash
gcloud auth login
gcloud config set project $gcp_project
```

DockerをGCPのArtifact Registryに登録します。

```bash
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
gcloud artifacts repositories create $image_name --location=asia-northeast1 --repository-format=docker --project=$gcp_project
```

Dockerイメージをビルドしてプッシュします。

```bash
docker rmi asia-northeast1-docker.pkg.dev/$gcp_project/$image_name/$image_name && docker rmi $image_name
docker build . -t $image_name --platform linux/amd64
docker tag $image_name asia-northeast1-docker.pkg.dev/$gcp_project/$image_name/$image_name && docker push asia-northeast1-docker.pkg.dev/$gcp_project/$image_name/$image_name:latest
```
