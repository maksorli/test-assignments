import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns


class Plotter:
    """
    A class to generate and save plots comparing ground truth and model predictions
    based on data from a JSON file.

    Attributes:
        data (pd.DataFrame): The data loaded from the provided JSON file.
        plot_dir (str): The directory where plots will be saved.
    """

    def __init__(self, json_path: str, plot_dir: str = "plots"):
        """
        Initializes the Plotter with the path to the JSON file and the directory
        for saving the plots.

        Args:
            json_path (str): The path to the JSON file containing the data.
            plot_dir (str): The directory to save the plots. Defaults to 'plots'.
        """
        self.data = pd.read_json(json_path)
        self.plot_dir = plot_dir

        # Create the directory if it doesn't exist
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)

    def draw_plots(self) -> list:
        """
        Draws and saves various plots comparing ground truth and predicted data.
        It also saves histograms for errors and a comparison of real vs predicted corners.

        Returns:
            list: A list of file paths where the plots have been saved.
        """
        # Path for the first plot comparing gt_corners and rb_corners
        plot_path = os.path.join(self.plot_dir, "corners_comparison.png")

        # Plot for comparing gt_corners and rb_corners
        plt.figure(figsize=(10, 6))
        plt.plot(self.data["gt_corners"], label="Ground Truth Corners")
        plt.plot(self.data["rb_corners"], label="Model Predicted Corners")
        plt.xlabel("Room Index")
        plt.ylabel("Number of Corners")
        plt.title("Ground Truth vs Model Predicted Corners")
        plt.legend()
        plt.savefig(plot_path)  # Save the plot first
        plt.show()  # Then display it
        plt.close()

        # Plot for error distribution (gt_corners - rb_corners)
        errors = self.data["gt_corners"] - self.data["rb_corners"]
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=20, color="orange")
        plt.xlabel("Prediction Error (Corners)")
        plt.ylabel("Frequency")
        plt.title("Distribution of Prediction Errors")
        error_plot_path = os.path.join(self.plot_dir, "prediction_error_histogram.png")
        plt.savefig(error_plot_path)  # Save the plot first
        plt.show()  # Then display it
        plt.close()

        # Transform data for the histogram comparison of real and predicted corners
        melted_data = pd.melt(
            self.data,
            value_vars=["gt_corners", "rb_corners"],
            var_name="Corner Type",
            value_name="Number of Corners",
        )

        # Print the first few rows of transformed data for verification
        print(melted_data.head())

        # Histogram comparing real and predicted corners
        plt.figure(figsize=(10, 6))
        sns.histplot(
            data=melted_data,
            stat="count",
            multiple="dodge",
            x="Number of Corners",
            kde=False,
            hue="Corner Type",
            palette="pastel",
            element="bars",
            legend=True,
        )
        plt.xlabel("Number of Corners")
        plt.ylabel("Count")
        plt.title("Distribution of Real vs Predicted Corners")
        hist_plot_path = os.path.join(self.plot_dir, "real_vs_predicted_corners.png")
        plt.savefig(hist_plot_path)  # Save the plot first
        plt.show()  # Then display it
        plt.close()

        # Return the paths to all saved plots
        return [plot_path, error_plot_path, hist_plot_path]
