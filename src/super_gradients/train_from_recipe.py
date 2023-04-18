"""
Entry point for training from a recipe using SuperGradients.

General use: python -m super_gradients.train_from_recipe --config-name="DESIRED_RECIPE".
For recipe's specific instructions and details refer to the recipe's configuration file in the recipes directory.
"""

from omegaconf import DictConfig
import hydra
import pkg_resources


@hydra.main(config_path=pkg_resources.resource_filename("super_gradients.recipes", ""), version_base="1.2")
def main(cfg: DictConfig) -> None:
    from super_gradients import Trainer

    Trainer.train_from_config(cfg)


def run():
    from super_gradients import init_trainer

    init_trainer()
    main()


if __name__ == "__main__":
    run()
