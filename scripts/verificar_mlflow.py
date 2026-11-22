import mlflow


def main():
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    experimento = mlflow.set_experiment(
        "Sistema de alerta temprana de volatilidad para acciones"
    )

    with mlflow.start_run(run_name="verificacion_tracking") as corrida:
        mlflow.set_tag("tipo", "verificacion_infraestructura")
        mlflow.log_param("prueba", "conexion_local")
        mlflow.log_text("MLflow recibió este artefacto.", "verificacion.txt")

        print("Experimento:", experimento.name)
        print("Run ID:", corrida.info.run_id)
        print("URI de artefactos:", mlflow.get_artifact_uri())


if __name__ == "__main__":
    main()