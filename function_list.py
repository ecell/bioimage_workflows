#import mlflow
import toml
import pathlib

#from generation import generation
from bioimage_workflow.toml import read_toml


def kaizu_generation(inputs: dict) -> str:
    seed = 123
    interval = 0.033
    num_samples = inputs["num_samples"]
    num_frames = inputs["num_frames"]
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
    print(inputs)
    artifacts = pathlib.Path("./artifacts")
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

    num_samples = inputs["num_samples"]
    num_frames = inputs["num_frames"]
    interval = 0.033
    generation_artifacts = pathlib.Path("./artifacts")
    
    import tempfile
    artifacts = pathlib.Path("./artifacts")
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

def kaizu_analysis2(inputs: dict, generation_artifacts: str, analysis1_artifacts: str) -> str:
    seed = inputs["seed"]
    max_distance = inputs["max_distance"]
    num_samples = inputs["num_samples"]
    num_frames = inputs["num_frames"]
    interval = inputs["interval"]

    import tempfile
    artifacts = pathlib.Path("./artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)

    #XXX: HERE

    import scopyon
    config = scopyon.Configuration(filename=generation_artifacts + "/config.yaml")
    pixel_length = config.default.detector.pixel_length / config.default.magnification

    import numpy

    def trace_spots(spots, max_distance=numpy.inf, ndim=2):
        observation_vec = []
        lengths = []
        for i in range(len(spots[0])):
            iprev = i
            for j in range(1, len(spots)):
                displacements = numpy.power(spots[j][:, : ndim] - spots[j - 1][iprev, : ndim], 2).sum(axis=1)
                inext = displacements.argmin()
                displacement = numpy.sqrt(displacements[inext])
                if displacement > max_distance:
                    if j > 1:
                        lengths.append(j - 1)
                    break
                intensity = spots[j - 1][iprev, ndim]
                observation_vec.append([displacement, intensity])
                iprev = inext
            else:
                lengths.append(len(spots) - 1)
        return observation_vec, lengths

    observation_vec = []
    lengths = []
    ndim = 2
    for i in range(num_samples):
        spots_ = numpy.load(analysis1_artifacts + "/" + f"spots{i:03d}.npy")
        t = spots_[0, 0]
        spots = [[spots_[0, 1: ]]]
        for row in spots_[1: ]:
            if row[0] == t:
                spots[-1].append(row[1: ])
            else:
                t = row[0]
                spots[-1] = numpy.asarray(spots[-1])
                spots.append([row[1: ]])
        else:
            spots[-1] = numpy.asarray(spots[-1])
        # print(spots)

        observation_vec_, lengths_ = trace_spots(spots, max_distance=max_distance, ndim=ndim)
        observation_vec.extend(observation_vec_)
        lengths.extend(lengths_)
    observation_vec = numpy.array(observation_vec)

    print(len(lengths), sum(lengths))

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=2, subplot_titles=['Square Displacement', 'Intensity'])
    fig.add_trace(go.Histogram(x=observation_vec[:, 0], nbinsx=30, histnorm='probability'), row=1, col=1)
    fig.add_trace(go.Histogram(x=observation_vec[:, 1], nbinsx=30, histnorm='probability'), row=1, col=2)
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75, showlegend=False)
    # fig.show()
    fig.write_image(str(artifacts / "histogram1.png"))

    from scopyon.analysis import PTHMM

    rng = numpy.random.RandomState(seed)
    model = PTHMM(n_diffusivities=3, n_oligomers=1, n_iter=100, random_state=rng)
    model.fit(observation_vec, lengths)
    
    print("diffusivities=\n", model.diffusivities_)
    print("D=\n", pixel_length ** 2 * model.diffusivities_ / interval / 1e-12)

    print("intensity_means=", model.intensity_means_)
    print("intensity_vars=", model.intensity_vars_)

    print("startprob=\n", model.startprob_)

    P = model.transmat_
    k = -numpy.log(1 - P) / interval
    k.ravel()[:: k.shape[0] + 1] = 0.0
    print("transmat=\n", model.transmat_)
    print("state_transition_matrix=\n", k)

    expected_vec = numpy.zeros((sum(lengths), 2), dtype=observation_vec.dtype)
    for i in range(len(lengths)):
        X_, Z_ = model.sample(lengths[i])
        expected_vec[sum(lengths[: i]): sum(lengths[: i + 1])] = X_

    fig = make_subplots(rows=1, cols=2, subplot_titles=['Square Displacement', 'Intensity'])
    fig.add_trace(go.Histogram(x=observation_vec[:, 0], nbinsx=30, histnorm='probability density'), row=1, col=1)
    fig.add_trace(go.Histogram(x=expected_vec[:, 0], nbinsx=30, histnorm='probability density'), row=1, col=1)
    fig.add_trace(go.Histogram(x=observation_vec[:, 1], nbinsx=30, histnorm='probability density'), row=1, col=2)
    fig.add_trace(go.Histogram(x=expected_vec[:, 1], nbinsx=30, histnorm='probability density'), row=1, col=2)
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75, showlegend=False)
    # fig.show()
    fig.write_image(str(artifacts / "histogram2.png"))

    #XXX: THERE
    return {"artifacts": artifacts.absolute().as_uri()}

