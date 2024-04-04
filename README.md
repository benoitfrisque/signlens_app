# SignLens - Deep Learning for Sign Language Classification

SignLens is a project that leverages the power of Deep Learning to classify American Sign Language (ASL) gestures. The project includes scripts for data preprocessing, model training, and prediction. It is a final project for the Data Science bootcamp at Le Wagon.

This repository hosts the frontend for the intuitive Streamlit interface, providing seamless accessibility: [SignLens Streamlit Interface](https://signlens.streamlit.app/)

## Deep Learning Classification Model

SignLens uses an approach where videos are initially transformed into JSON files containing [Mediapipe](https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md) landmarks. Subsequently, these JSON files are transmitted to an API housing the landmark model, which returns accurate classifications. The development of both the model and the API is detailed [here](https://github.com/benoitfrisque/signlens).


## Authors

- [Benoît Frisque](https://github.com/benoitfrisque)
- [Wail Benrabh](https://github.com/WailBen97)
- [Jan Storz](https://github.com/janstorz)
- [Maximilien Grieb](https://github.com/MaxGrieb)

## Contact

If you have any questions, comments, or feedback, feel free to reach out to us!

- Email: benoitfrisque@gmail.com
- GitHub: [benoitfrisque](https://github.com/benoitfrisque)
