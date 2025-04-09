# -*- coding: utf-8 -*-
"""
Thermalift, version 1.0.2
Last updated on April 9, 2025

author: Maciej Miecznik
affiliation: Mineral and Energy Economy Research Institute,
             Polish Academy of Sciences
             Wybickiego 7A, 31-261 Kraków, Poland
e-mail: miecznik@min-pan.krakow.pl

purpose: this code performs calculation to eliminate the
effect of thermal lift from the raw data of recorded wellhead
pressure / water level in geothermal wells. Records without
the noise caused by thermal lift can be used for better
assessment of the true drawdown - hence, for better evaluation
of true reservoir transmissivity (hydraulic characterization)
or production model calibration
"""

import brine_density
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class Formation:
    def __init__(self, formation_temp_file):
        self.formation_temp_file = formation_temp_file

    def read_formation_data(self):
        formation = pd.read_csv(self.formation_temp_file, sep=";", decimal=".")
        return formation

    def temp_interpolation(self, zmin, zmax, dz, method="cubic"):
        formation_old = self.read_formation_data()

        depth_new = pd.Series(
            np.arange(zmin, zmax, dz), name=formation_old.columns[0]
        )

        # create new dataframe to collect interpolated temperature of the formation
        formation_new = pd.merge(
            formation_old,
            depth_new,
            on=formation_old.columns[0],
            how="outer",
        )

        # interpolate temperature using chosen method
        formation_new.interpolate(method=method, inplace=True)
        formation_new.dropna(axis=0, inplace=True)

        print(
            "Average temperature of the formation before interpolation was ",
            formation_old["Temp"].mean(),
            "deg. C",
        )
        print(
            "Average temperature of the formation after interpolation is ",
            formation_new["Temp"].mean(),
            "deg. C",
        )
        return formation_new

    def formation_temperature_plot(self, formation, formation_new):
        fig, axs = plt.subplots(1, figsize=(8, 8), layout="constrained")
        axs.plot(
            formation_new["Temp"],
            formation_new["Depth"],
            linewidth=2,
            color="red",
            label="interpolation",
        )
        axs.scatter(
            formation["Temp"],
            formation["Depth"],
            color="orange",
            label="measurements",
        )
        axs.set_xticks(np.arange(0, formation_new["Temp"].max() + 5, 5))
        axs.set_yticks(np.arange(0, formation_new["Depth"].max() + 250, 250))
        axs.invert_yaxis()
        axs.grid(True)
        axs.set_xlabel("Temperature [°C]", fontsize=12)
        axs.set_ylabel("Measured depth [m]", fontsize=12)
        axs.legend(loc="lower left")
        fig.suptitle(
            "Interpolated temperature along well`s curvature", fontsize=16
        )

        plt.savefig("rock_formation_temperature.png", dpi=300)


class Well:

    def __init__(self, pumping_input, name="", salinity=0.0):
        self.pumping_input = pumping_input
        self.name = name
        self.salinity = salinity

    # Calculate mean static temperature in the water column
    # Well not pumped

    def temp_static(self, formation_temp):
        return formation_temp.iloc[:, 1].mean()

    # Calculate mean temperature in the flowing well
    def temp_flowing(
        self, formation_temp, temp_col, pumping_input, wellhead_temp_col
    ):
        return (
            formation_temp.iloc[:, temp_col].max()
            + pumping_input.iloc[:, wellhead_temp_col]
        ) / 2

    # Calculate mean water column density in a non-flowing well
    def dens_static(self, mean_temp_static, salinity):
        return brine_density.brine_density(mean_temp_static, salinity)

    # Calculate mean water column density in a flowing well
    def dens_dynamic(self, mean_temp_flowing, salinity):
        return brine_density.brine_density(mean_temp_flowing, salinity)

    # Convert pressure records to water level
    def water_level(
        self, pressure_level, flow_dens, probe_depth, atmo_pressure
    ):
        water_level = probe_depth - (pressure_level * 1e5 - atmo_pressure) / (
            9.81 * flow_dens
        )
        return water_level

    # Calculate measured drawdown
    def measured_drawdown(self, water_level):
        rec_drawdown = water_level - water_level.min()
        return rec_drawdown

    # Calculate the true water level, after eliminating thermal lift
    def true_water_level(self, water_level, flow_dens, stat_dens, depth_max):
        true_water_level = (
            water_level + (1 - flow_dens / stat_dens) * depth_max
        )
        return true_water_level

    # Calculate true drawdown, after eliminating thermal lift
    def true_drawdown(self, true_water_level):
        true_drawdown = true_water_level - true_water_level.min()
        return true_drawdown

    # Define type of fitting function
    def polynomial(self, x, a, b, c):
        return a * x**2 + b * x + c

    # Calculate polynomial fitting
    def polyfit(self, x, y, bounds=False):
        # exclude values that are NaN or infinity
        idx = np.isfinite(x) & np.isfinite(y)
        x = np.asarray(x[idx], dtype="object")
        y = np.asarray(y[idx], dtype="object")

        if bounds is False:
            popt, pcov = curve_fit(self.polynomial, x, y)
        else:
            popt, pcov = curve_fit(
                self.polynomial,
                x,
                y,
                bounds=(0, np.inf),
            )
        return popt

    def r_square(self, x, y):
        # exclude values that are NaN or infinity
        idx = np.isfinite(x) & np.isfinite(y)
        x = np.asarray(x[idx], dtype="object")
        y = np.asarray(y[idx], dtype="object")

        # Calculate R^2 coeff.
        residuals = x - y
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot
        print("R^2 = ", r_squared)
        return r_squared

    def rmse(self, x, y):
        # exclude values that are NaN or infinity
        idx = np.isfinite(x) & np.isfinite(y)
        x = np.asarray(x[idx], dtype="object")
        y = np.asarray(y[idx], dtype="object")

        residuals = x - y
        ss_res = np.sum(residuals**2)
        rmse = (ss_res / len(y)) ** 0.5
        print("RMSE = ", rmse)
        return rmse

    def save_results(self, filename):
        results_list = [
            self.pumping_input.iloc[:, 0].to_list(),
            self.pumping_input.iloc[:, 6].to_list(),
            self.mean_flowing_temp.to_list(),
            self.mean_flowing_dens.to_list(),
            self.water_level.to_list(),
            self.true_water_level.to_list(),
            self.recorded_drawdown.to_list(),
            self.true_drawdown.to_list(),
        ]

        res = [list(row) for row in zip(*results_list)]

        results_df = pd.DataFrame(
            res,
            columns=[
                "Date",
                "Flowrate",
                "MeanFlowingTemp",
                "MeanFlowingDens",
                "RecWaterLev",
                "CorrWaterLev",
                "RecDrawdown",
                "CorrDrawdown",
            ],
        )
        results_df.to_excel(filename, index=False)

    def raw_data_plot(
        self,
        time,
        flowrate,
        temperature,
        water_level,
        title="",
        figsize=(16, 10),
    ):

        fig, axs = plt.subplots(
            nrows=3, ncols=1, figsize=figsize, layout="constrained"
        )

        axs[0].plot(time, flowrate, c="blue", label="flow rate")
        axs[0].set_ylabel("Flow rate [$m^3$/h]", fontsize=12)
        axs[1].plot(time, water_level, c="green", label="recorded water level")
        axs[1].set_ylabel("Water level [m b.g.l.]", fontsize=12)
        axs[2].plot(time, temperature, c="red", label="wellhead temperature")
        axs[2].set_ylabel("Temperature [°C]", fontsize=12)
        axs[1].sharex(axs[0])
        axs[2].sharex(axs[0])

        for ax in axs:
            ax.grid(True)

        plt.suptitle(title, fontsize=16)
        plt.show()
        plt.savefig(title + "_pumping_raw_data.png", dpi=300)

    # Create mosaic plot comparing data before and after thermal lift correction
    def mosaic_plot(
        self,
        time,
        flowrate,
        temperature,
        density,
        water_level,
        corrected_water_level,
        recorded_drawdown,
        corrected_drawdown,
        bounds=True,
        show_fit=False,
        title="",
        figsize=(25, 12),
    ):
        fig, axs = plt.subplot_mosaic(
            [
                ["flowrate", "drawdawn_vs_flowrate"],
                ["temperature", "drawdawn_vs_flowrate"],
                ["density", "drawdawn_vs_flowrate"],
                ["water_level", "drawdawn_vs_flowrate"],
                ["drawdown", "drawdawn_vs_flowrate"],
            ],
            layout="constrained",
            width_ratios=[2, 1.3],
            figsize=figsize,
        )

        axs["flowrate"].plot(time, flowrate, c="blue", label="flow rate")
        axs["flowrate"].grid(True)
        axs["flowrate"].set_ylabel("Flow rate [$m^3$/h]", fontsize=12)
        axs["flowrate"].legend(loc="lower left")

        axs["temperature"].plot(
            time,
            temperature,
            c="red",
            label="mean temperature of water column in the flowing well",
        )
        axs["temperature"].grid(True)
        axs["temperature"].set_ylabel("Temperature [°C]", fontsize=12)
        axs["temperature"].legend(loc="lower left")
        axs["temperature"].sharex(axs["flowrate"])

        axs["density"].plot(
            time,
            density,
            c="orange",
            label="mean density of water column in the flowing well",
        )
        axs["density"].grid(True)
        axs["density"].set_ylabel("Density[kg/$m^3$]", fontsize=12)
        axs["density"].legend(loc="lower left")
        axs["density"].sharex(axs["flowrate"])

        axs["water_level"].plot(
            time, water_level, c="green", label="recorded water level"
        )
        axs["water_level"].plot(
            time,
            corrected_water_level,
            c="limegreen",
            label="corrected water level",
        )
        axs["water_level"].grid(True)
        axs["water_level"].set_ylabel("Water level [m b.g.l.]", fontsize=12)
        axs["water_level"].invert_yaxis()
        axs["water_level"].legend(loc="lower left")
        axs["water_level"].sharex(axs["flowrate"])

        axs["drawdown"].plot(
            time, recorded_drawdown, c="dodgerblue", label="recorded drawdown"
        )
        axs["drawdown"].plot(
            time, corrected_drawdown, c="navy", label="corrected drawdown"
        )
        axs["drawdown"].grid(True)
        axs["drawdown"].set_ylabel("Drawdown [m]", fontsize=12)
        axs["drawdown"].invert_yaxis()
        axs["drawdown"].legend(loc="lower left")
        axs["drawdown"].sharex(axs["flowrate"])

        axs["drawdawn_vs_flowrate"].scatter(
            flowrate,
            recorded_drawdown,
            c="tomato",
            label="recorded drawdown",
            s=20,
        )

        axs["drawdawn_vs_flowrate"].scatter(
            flowrate,
            corrected_drawdown,
            c="navy",
            label="true drawdown",
            s=20,
        )

        if show_fit is True:

            # Calculate polynomial fitting between the flowrate and the drawdown
            rec_drawdown_polyfit = self.polyfit(
                flowrate, recorded_drawdown, bounds=bounds
            )
            true_drawdown_polyfit = self.polyfit(
                flowrate, corrected_drawdown, bounds=bounds
            )

            axs["drawdawn_vs_flowrate"].plot(
                np.arange(0, 260, 5),
                np.polyval(rec_drawdown_polyfit, np.arange(0, 260, 5)),
                c="red",
                linewidth=3,
                linestyle="dotted",
                label="recorded drawdown fit",
            )
            axs["drawdawn_vs_flowrate"].text(
                flowrate.max() * 0.6,
                recorded_drawdown.mean() * 0.4,
                "s = {:1.2e}*Q^2 + {:1.2e}*Q + {:2.2f}\n$R^2$ = {:1.2f}\nRMSE = {:1.2f}".format(
                    rec_drawdown_polyfit[0],
                    rec_drawdown_polyfit[1],
                    rec_drawdown_polyfit[2],
                    self.r_square(
                        np.polyval(rec_drawdown_polyfit, flowrate),
                        recorded_drawdown,
                    ),
                    self.rmse(
                        np.polyval(rec_drawdown_polyfit, flowrate),
                        recorded_drawdown,
                    ),
                ),
                fontsize=11,
                color="red",
            )

            axs["drawdawn_vs_flowrate"].plot(
                np.arange(0, 260, 5),
                np.polyval(true_drawdown_polyfit, np.arange(0, 260, 5)),
                c="blue",
                linewidth=3,
                linestyle="dotted",
                label="corrected drawdown fit",
            )
            axs["drawdawn_vs_flowrate"].text(
                flowrate.max() * 0.6,
                corrected_drawdown.max() * 1.1,
                "s = {:1.2e}*Q^2 + {:1.2e}*Q + {:2.2f}\n$R^2$ = {:1.2f}\nRMSE = {:1.2f}".format(
                    true_drawdown_polyfit[0],
                    true_drawdown_polyfit[1],
                    true_drawdown_polyfit[2],
                    self.r_square(
                        np.polyval(true_drawdown_polyfit, flowrate),
                        corrected_drawdown,
                    ),
                    self.rmse(
                        np.polyval(true_drawdown_polyfit, flowrate),
                        corrected_drawdown,
                    ),
                ),
                fontsize=11,
                color="navy",
            )
        else:
            pass

        axs["drawdawn_vs_flowrate"].grid(True)
        axs["drawdawn_vs_flowrate"].set_ylim(0, 150)
        axs["drawdawn_vs_flowrate"].invert_yaxis()
        axs["drawdawn_vs_flowrate"].set_xlabel(
            "Flow rate [$m^3$/h]", fontsize=12
        )
        axs["drawdawn_vs_flowrate"].set_ylabel("Drawdown [m]", fontsize=12)
        axs["drawdawn_vs_flowrate"].legend(loc="lower left")

        plt.suptitle(title, fontsize=16)
        plt.show()
        plt.savefig(title + "_thermal_lift.png", dpi=300)
