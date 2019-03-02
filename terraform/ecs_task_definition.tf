data "aws_ecr_repository" "web" {
  name = "${var.project_safe_name}/${var.ecr_repo_web_primary_name}"

  # other available vars exposed: (https://www.terraform.io/docs/providers/aws/d/ecr_repository.html)
  # arn
  # registry_id
  # repository_url
  # tags
}

data "aws_ecr_repository" "nginx" {
  name = "${var.project_safe_name}/${var.ecr_repo_nginx_primary_name}"
}

data "aws_ecs_task_definition" "test" {
  task_definition = "${aws_ecs_task_definition.test.family}"
  depends_on      = ["aws_ecs_task_definition.test"]
}

resource "aws_ecs_task_definition" "test" {
  family                   = "${var.project_name}-family"
  network_mode             = "bridge"                                      # The valid values are none, bridge, awsvpc, and host. The default Docker network mode is bridge.
  requires_compatibilities = ["EC2"]
  execution_role_arn       = "${data.aws_iam_role.ecs-task-execution.arn}" # required if container secret

  # json injection using EOF: https://github.com/terraform-providers/terraform-provider-aws/issues/3970
  # json injection using JSON: https://github.com/terraform-providers/terraform-provider-aws/issues/632
  # aws spec: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
  # aws wizard setup: https://medium.freecodecamp.org/how-to-deploy-a-node-js-application-to-amazon-web-services-using-docker-81c2a2d7225b
  container_definitions = <<JSON
[
     {
      "name": "${var.task_container_name_nginx}",
      "image": "${data.aws_ecr_repository.nginx.repository_url}:${var.ecr_new_image_tag}",
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${data.aws_cloudwatch_log_group.main.name}",
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "ecs-${var.task_container_name_nginx}"
        }
      },
      "portMappings": [
        {
          "hostPort": 80,
          "protocol": "tcp",
          "containerPort": 80
        }
      ],
      "command": [],
      "cpu": 64,
      "environment": [],
      "mountPoints": [
        {
          "readOnly": false,
          "containerPath": "/usr/src/django/global_static",
          "sourceVolume": "global_static"
        }
      ],
      "dockerSecurityOptions": [],
      "memory": null,
      "memoryReservation": 64,
      "volumesFrom": [],
      "healthCheck": {
        "retries": 3,
        "command": [
          "CMD-SHELL",
          "exit 0"
        ],
        "timeout": 5,
        "interval": 10,
        "startPeriod": null
      },
      "essential": true,
      "links": ["${var.task_container_name_web}"],
      "privileged": false
    },





    {
      "name": "${var.task_container_name_web}",
      "image": "${data.aws_ecr_repository.web.repository_url}:${var.ecr_new_image_tag}",
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${data.aws_cloudwatch_log_group.main.name}",
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "ecs-${var.task_container_name_web}"
        }
      },
      "command": [],
      "cpu": 64,
      "mountPoints": [
        {
          "readOnly": false,
          "containerPath": "/usr/src/django/global_static",
          "sourceVolume": "global_static"
        }
      ],
      "environment": [
        {
          "name": "DATABASE",
          "value": "postgres"
        },
        {
          "name": "SQL_ENGINE",
          "value": "django.db.backends.postgresql"
        },
        {
          "name": "SQL_PORT",
          "value": "5432"
        }
      ],
      "secrets": [
        {
          "name": "DJANGO_SECRET_KEY",
          "valueFrom": "${data.aws_ssm_parameter.dj-secret-key.arn}"
        },
        {
          "name": "SQL_DATABASE",
          "valueFrom": "${data.aws_ssm_parameter.sql-db.arn}"
        },
        {
          "name": "SQL_HOST",
          "valueFrom": "${data.aws_ssm_parameter.sql-host.arn}"
        },
        {
          "name": "SQL_PASSWORD",
          "valueFrom": "${data.aws_ssm_parameter.sql-pw.arn}"
        },
        {
          "name": "SQL_USER",
          "valueFrom": "${data.aws_ssm_parameter.sql-user.arn}"
        }
      ],
      "dockerSecurityOptions": [],
      "memory": null,
      "memoryReservation": 64,
      "volumesFrom": [],
      "essential": true,
      "privileged": false,
      "healthCheck": {
        "retries": 1,
        "command": [
          "CMD-SHELL",
          "exit 0 || curl -f http://localhost/ || exit 1"
        ],
        "timeout": 5,
        "interval": 10,
        "startPeriod": null
      },
      "links": ["${var.task_container_name_db}"]
    },






    {
      "name": "${var.task_container_name_db}",
      "dnsSearchDomains": null,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${data.aws_cloudwatch_log_group.main.name}",
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "ecs-${var.task_container_name_db}"
        }
      },
      "entryPoint": null,
      "portMappings": null,
      "command": null,
      "linuxParameters": null,
      "cpu": 16,
      "resourceRequirements": null,
      "ulimits": null,
      "dnsServers": null,
      "mountPoints": [
        {
          "readOnly": false,
          "containerPath": "/var/lib/postgresql/data/",
          "sourceVolume": "postgres_data"
        }
      ],
      "workingDirectory": null,
      "environment": [
        {
          "name": "POSTGRES_DATA",
          "value": "/var/lib/postgresql/data/"
        }
      ],
      "secrets": [
        {
          "name": "POSTGRES_PASSWORD",
          "valueFrom": "${data.aws_ssm_parameter.sql-pw.arn}"
        },
        {
          "name": "POSTGRES_USER",
          "valueFrom": "${data.aws_ssm_parameter.sql-user.arn}"
        },
        {
          "name": "POSTGRES_DB",
          "valueFrom": "${data.aws_ssm_parameter.sql-db.arn}"
        }
      ],
      "memory": null,
      "memoryReservation": 16,
      "image": "postgres:10.5-alpine",
      "healthCheck": null,
      "essential": true,
      "links": null,
      "hostname": null,
      "extraHosts": null,
      "pseudoTerminal": null,
      "user": null,
      "readonlyRootFilesystem": null,
      "dockerLabels": null,
      "systemControls": null
    }
]
JSON

  volume {
    name      = "global_static"
    host_path = "/opt/global_static"
  }

  volume {
    name      = "postgres_data"
    host_path = "/opt/postgres_data"
  }

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-east-2a, us-east-2b]"
  }

  depends_on = [
    "data.aws_ecr_repository.nginx",
    "data.aws_ecr_repository.web",
    "null_resource.aws_ecs_task_definition__test_var_dependency",
  ]
}

resource "null_resource" "aws_ecs_task_definition__test_var_dependency" {
  triggers {
    task_container_name_nginx = "${var.task_container_name_nginx}"
    task_container_name_web   = "${var.task_container_name_web}"
    task_container_name_db    = "${var.task_container_name_db}"
  }
}
