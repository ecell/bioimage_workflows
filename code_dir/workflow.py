#import mlflow
import toml
import pathlib

#from generation import generation
from tomlfunc import get_inputs

def try_generation():
    tomlfile = "./test.toml"
    outputs = generation(get_inputs(tomlfile))
    return outputs

def kaizu_generation(inputs: dict) -> str:
    seed = 123
    interval = 0.033
    num_samples = 1
    num_frames = 2
    exposure_time = 0.033

    Nm = [100, 100, 100]
    Dm = [0.222e-12, 0.032e-12, 0.008e-12]
    transmat = [
        [0.0, 0.5, 0.0],
        [0.5, 0.0, 0.2],
        [0.0, 1.0, 0.0]]

    # for key, value in vars(args).items():
    #     log_param(key, value)

    import tempfile
    artifacts = pathlib.Path(tempfile.mkdtemp()) / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    #XXX: HERE

    import numpy
    rng = numpy.random.RandomState(seed)

    import scopyon

    config = scopyon.DefaultConfiguration()
    config.default.effects.photo_bleaching.switch = False
    config.default.detector.exposure_time = exposure_time
    pixel_length = config.default.detector.pixel_length / config.default.magnification
    L_2 = config.default.detector.image_size[0] * pixel_length * 0.5
    L_2

    timepoints = numpy.linspace(0, interval * num_frames, num_frames + 1)
    ndim = 2

    config.save(artifacts / 'config.yaml')

    for i in range(num_samples):
        samples = scopyon.sample(timepoints, N=Nm, lower=-L_2, upper=+L_2, ndim=ndim, D=Dm, transmat=transmat, rng=rng)
        inputs = [(t, numpy.hstack((points[:, : ndim], points[:, [ndim + 1]], numpy.ones((points.shape[0], 1), dtype=numpy.float64)))) for t, points in zip(timepoints, samples)]
        ret = list(scopyon.generate_images(inputs, num_frames=num_frames, config=config, rng=rng, full_output=True))

        inputs_ = []
        for t, data in inputs:
            inputs_.extend(([t] + list(row) for row in data))
        inputs_ = numpy.array(inputs_)
        numpy.save(artifacts / f"inputs{i:03d}.npy", inputs_)

        numpy.save(artifacts / f"images{i:03d}.npy", numpy.array([img.as_array() for img, infodict in ret]))
        ret[0][0].save(artifacts / f"image{i:03d}_000.png")

        true_data = []
        for t, (_, infodict) in zip(timepoints, ret):
            true_data.extend([t, key] + list(value) for key, value in infodict['true_data'].items())
        true_data = numpy.array(true_data)
        numpy.save(artifacts / f"true_data{i:03d}.npy", true_data)

    return artifacts.absolute().as_uri()

def kaizu_analysis1(inputs: dict) -> str:

    generation = ""
    min_sigma = 1
    max_sigma = 4
    threshold = 50.0
    overlap = 0.5

    num_samples = 1
    num_frames = 2
    interval = 0.033
    generation_artifacts = pathlib.Path("/tmp/tmp0j3ulrlj/artifacts")

    import tempfile
    artifacts = pathlib.Path(tempfile.mkdtemp()) / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    #XXX: HERE

    import numpy
    timepoints = numpy.linspace(0, interval * num_frames, num_frames + 1)

    import scopyon

    import warnings
    warnings.simplefilter('ignore', RuntimeWarning)

    for i in range(num_samples):
        imgs = [scopyon.Image(data) for data in numpy.load(generation_artifacts / f"images{i:03d}.npy")]
        spots = [
            scopyon.analysis.spot_detection(
                img.as_array(),
                min_sigma=min_sigma, max_sigma=max_sigma, threshold=threshold, overlap=overlap)
            for img in imgs]

        spots_ = []
        for t, data in zip(timepoints, spots):
            spots_.extend(([t] + list(row) for row in data))
        spots_ = numpy.array(spots_)
        numpy.save(artifacts / f"spots{i:03d}.npy", spots_)

        r = 6
        shapes = [dict(x=spot[0], y=spot[1], sigma=r, color='red')
                for spot in spots[0]]
        imgs[0].save(artifacts / f"spots{i:03d}_000.png", shapes=shapes)

        print("{} spots are detected in {} frames.".format(len(spots_), len(imgs)))
        #log_metric("num_spots", len(spots_))

    return {"artifacts": artifacts.absolute().as_uri(), "num_spots": len(spots_)}
