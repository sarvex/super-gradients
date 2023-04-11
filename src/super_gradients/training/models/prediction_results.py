from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Iterator
from dataclasses import dataclass

import numpy as np

from super_gradients.training.utils.detection_utils import DetectionVisualization
from super_gradients.training.models.predictions import Prediction, DetectionPrediction
from super_gradients.training.utils.media.video import show_video_from_frames
from super_gradients.training.utils.media.image import show_image


@dataclass
class ImagePrediction(ABC):
    """Object wrapping an image and a model's prediction.

    :attr image:        Input image
    :attr predictions:  Predictions of the model
    :attr class_names:  List of the class names to predict
    """

    image: np.ndarray
    prediction: Prediction
    class_names: List[str]

    @abstractmethod
    def draw(self) -> np.ndarray:
        """Draw the predictions on the image."""
        pass

    @abstractmethod
    def show(self) -> None:
        """Display the predictions on the image."""
        pass


@dataclass
class ImageDetectionPrediction(ImagePrediction):
    """Object wrapping an image and a detection model's prediction.

    :attr image:        Input image
    :attr predictions:  Predictions of the model
    :attr class_names:  List of the class names to predict
    """

    image: np.ndarray
    prediction: DetectionPrediction
    class_names: List[str]

    def draw(self, box_thickness: int = 2, show_confidence: bool = True, color_mapping: Optional[List[Tuple[int]]] = None) -> np.ndarray:
        """Draw the predicted bboxes on the image.

        :param box_thickness:   Thickness of bounding boxes.
        :param show_confidence: Whether to show confidence scores on the image.
        :param color_mapping:   List of tuples representing the colors for each class.
                                Default is None, which generates a default color mapping based on the number of class names.
        :return:                Image with predicted bboxes. Note that this does not modify the original image.
        """
        image_np = self.image.copy()
        color_mapping = color_mapping or DetectionVisualization._generate_color_mapping(len(self.class_names))

        for pred_i in range(len(self.prediction)):
            image_np = DetectionVisualization._draw_box_title(
                color_mapping=color_mapping,
                class_names=self.class_names,
                box_thickness=box_thickness,
                image_np=image_np,
                x1=int(self.prediction.bboxes_xyxy[pred_i, 0]),
                y1=int(self.prediction.bboxes_xyxy[pred_i, 1]),
                x2=int(self.prediction.bboxes_xyxy[pred_i, 2]),
                y2=int(self.prediction.bboxes_xyxy[pred_i, 3]),
                class_id=int(self.prediction.labels[pred_i]),
                pred_conf=self.prediction.confidence[pred_i] if show_confidence else None,
            )
        return image_np

    def show(self, box_thickness: int = 2, show_confidence: bool = True, color_mapping: Optional[List[Tuple[int]]] = None) -> None:
        """Display the image with predicted bboxes.

        :param box_thickness:   Thickness of bounding boxes.
        :param show_confidence: Whether to show confidence scores on the image.
        :param color_mapping:   List of tuples representing the colors for each class.
                                Default is None, which generates a default color mapping based on the number of class names.
        """
        image_np = self.draw(box_thickness=box_thickness, show_confidence=show_confidence, color_mapping=color_mapping)
        show_image(image_np)


@dataclass
class ImagesPredictions(ABC):
    """Object wrapping the list of image predictions.

    :attr _images_prediction_lst: List of results of the run
    """

    _images_prediction_lst: List[ImagePrediction]

    def __len__(self) -> int:
        return len(self._images_prediction_lst)

    def __getitem__(self, index: int) -> ImagePrediction:
        return self._images_prediction_lst[index]

    def __iter__(self) -> Iterator[ImagePrediction]:
        return iter(self._images_prediction_lst)

    @abstractmethod
    def show(self) -> None:
        pass


@dataclass
class VideoPredictions(ImagesPredictions, ABC):
    """Object wrapping the list of image predictions as a Video.

    :attr _images_prediction_lst:   List of results of the run
    :att fps:                       Frames per second of the video
    """

    _images_prediction_lst: List[ImagePrediction]
    fps: float

    @abstractmethod
    def show(self, *args, **kwargs) -> None:
        """Display the predictions on the image."""
        pass


@dataclass
class ImagesDetectionPrediction(ImagesPredictions):
    """Object wrapping the list of image detection predictions.

    :attr _images_prediction_lst:  List of the predictions results
    """

    _images_prediction_lst: List[ImageDetectionPrediction]

    def show(self, box_thickness: int = 2, show_confidence: bool = True, color_mapping: Optional[List[Tuple[int]]] = None) -> None:
        """Display the predicted bboxes on the images.

        :param box_thickness:   Thickness of bounding boxes.
        :param show_confidence: Whether to show confidence scores on the image.
        :param color_mapping:   List of tuples representing the colors for each class.
                                Default is None, which generates a default color mapping based on the number of class names.
        """
        for prediction in self._images_prediction_lst:
            prediction.show(box_thickness=box_thickness, show_confidence=show_confidence, color_mapping=color_mapping)


@dataclass
class VideoDetectionPrediction(VideoPredictions):
    """Object wrapping the list of image detection predictions as a Video.

    :attr _images_prediction_lst:  List of the predictions results
    :att fps:                       Frames per second of the video
    """

    _images_prediction_lst: List[ImageDetectionPrediction]
    fps: float

    def show(self, box_thickness: int = 2, show_confidence: bool = True, color_mapping: Optional[List[Tuple[int]]] = None) -> None:
        """Display the predicted bboxes on the images.

        :param box_thickness:   Thickness of bounding boxes.
        :param show_confidence: Whether to show confidence scores on the image.
        :param color_mapping:   List of tuples representing the colors for each class.
                                Default is None, which generates a default color mapping based on the number of class names.
        """
        frames = [
            result.draw(box_thickness=box_thickness, show_confidence=show_confidence, color_mapping=color_mapping) for result in self._images_prediction_lst
        ]
        show_video_from_frames(window_name="Detection", frames=frames, fps=self.fps)
