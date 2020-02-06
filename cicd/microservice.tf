# variables are expected to be fed via environment variables or cli args
variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}
variable "app_container_image_tag" {}

module "appl_tracky_api" {
  source  = "rivernews/kubernetes-microservice/digitalocean"
  version = "v0.0.5"

  aws_region     = var.aws_region
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  cluster_name   = "project-shaungc-digitalocean-cluster"

  app_label               = "appl-tracky-api"
  app_exposed_port        = 8001
  app_deployed_domain     = "appl-tracky.api.shaungc.com"
  cors_domain_whitelist   = ["rivernews.github.io", "appl-tracky.shaungc.com"]
  app_container_image     = "shaungc/appl-tracky-api"
  app_container_image_tag = var.app_container_image_tag
  app_secret_name_list = [
    "/provider/aws/account/iriversland2-15pro/AWS_REGION",
    "/provider/aws/account/iriversland2-15pro/AWS_ACCESS_KEY_ID",
    "/provider/aws/account/iriversland2-15pro/AWS_SECRET_ACCESS_KEY",

    "/app/appl-tracky/DJANGO_SECRET_KEY",
    "/app/appl-tracky/ADMINS",

    "/app/appl-tracky/SQL_ENGINE",
    "/app/appl-tracky/SQL_DATABASE",
    "/database/postgres_cluster_kubernetes/SQL_USER",
    "/database/postgres_cluster_kubernetes/SQL_PASSWORD",
    "/database/postgres_cluster_kubernetes/SQL_HOST",
    "/database/postgres_cluster_kubernetes/SQL_PORT",

    "/database/elasticsearch_cluster_kubernetes/ELASTICSEARCH_HOST",
    "/database/elasticsearch_cluster_kubernetes/ELASTICSEARCH_PORT",

    "/database/redis_cluster_kubernetes/REDIS_HOST",
    "/database/redis_cluster_kubernetes/REDIS_PORT",
    "/app/appl-tracky/CACHEOPS_REDIS_DB",

    "/service/gmail/EMAIL_HOST",
    "/service/gmail/EMAIL_HOST_USER",
    "/service/gmail/EMAIL_HOST_PASSWORD",
    "/service/gmail/EMAIL_PORT",

    "/service/google-social-auth/SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
    "/service/google-social-auth/SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
  ]
  kubernetes_cron_jobs = [
    {
      name          = "db-backup-cronjob",

      # every day 11:00pm PST, to avoid the maintenance windown of digitalocean in 12-4am
      cron_schedule = "0 6 * * *", 

      command = ["/bin/sh", "-c", "echo Starting cron job... && sleep 5 && cd /usr/src/django && echo Finish CD && python manage.py backup_db && echo Finish dj command"]
    },
  ]

  depend_on = [
    # module.postgres_cluster.app_container_image,
    # module.redis_cluster.app_container_image
  ]
}