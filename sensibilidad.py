
"""
sensibilidad.py
Barrido de parámetros c y λ para análisis de sensibilidad.
"""


from montecarlo import correr_replicas


def analisis_sensibilidad(lam_valores, c_valores, mu=4, T_sim=480,
                           T_warm=60, N=30):
    """
    Ejecuta Montecarlo para cada combinación (lam, c).
    Retorna tabla de resultados como lista de diccionarios.
    """
    tabla = []
    total = len(lam_valores) * len(c_valores)
    i = 0

    for c in c_valores:
        for lam in lam_valores:
            rho = lam / (c * mu)
            i += 1
            print(f"  [{i}/{total}] c={c}, λ={lam}, ρ={rho:.3f} ...", end=" ")

            if rho >= 1:
                print("INESTABLE — omitido")
                tabla.append({
                    "c": c, "lam": lam, "rho": rho,
                    "Wq_media": None, "Lq_media": None
                })
                continue

            res = correr_replicas(N=N, lam=lam, mu=mu, c=c,
                                  T_sim=T_sim, T_warm=T_warm)
            Lq = res["Wq_media"] * lam / 60  # Ley de Little: Lq = λ * Wq
            print(f"Wq={res['Wq_media']:.2f} min, Lq={Lq:.3f}")

            tabla.append({
                "c"       : c,
                "lam"     : lam,
                "rho"     : rho,
                "Wq_media": res["Wq_media"],
                "Lq_media": Lq,
            })

    return tabla


def imprimir_tabla(tabla):
    print("\n{'c':>4} {'λ':>6} {'ρ':>6} {'Wq(min)':>10} {'Lq':>8}")
    print("-" * 40)
    for fila in tabla:
        if fila["Wq_media"] is None:
            print(f"{fila['c']:>4} {fila['lam']:>6} {fila['rho']:>6.3f} {'INESTABLE':>10}")
        else:
            print(f"{fila['c']:>4} {fila['lam']:>6} {fila['rho']:>6.3f} "
                  f"{fila['Wq_media']:>10.2f} {fila['Lq_media']:>8.3f}")


if __name__ == "__main__":
    lam_valores = [6, 8, 10, 11, 12]
    c_valores   = [2, 3, 4, 5]

    print("Ejecutando análisis de sensibilidad...")
    tabla = analisis_sensibilidad(lam_valores, c_valores)
    imprimir_tabla(tabla)