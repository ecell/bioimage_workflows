import mlflow
from mlflow import log_metric, log_param, log_artifacts

import argparse
parser = argparse.ArgumentParser(description='generation step')
parser.add_argument('--seed', type=int, default=123)
parser.add_argument('--interval', type=float, default=33e-3)
parser.add_argument('--num_samples', type=int, default=1)
parser.add_argument('--num_frames', type=int, default=5)
parser.add_argument('--exposure_time', type=float, default=0.033)
args = parser.parse_args()

run_obj = mlflow.start_run(run_name="generation")

seed = args.seed
interval = args.interval
num_samples = args.num_samples
num_frames = args.num_frames
exposure_time = args.exposure_time

Nm = [100, 100, 100]
Dm = [0.222e-12, 0.032e-12, 0.008e-12]
transmat = [
    [0.0, 0.5, 0.0],
    [0.5, 0.0, 0.2],
    [0.0, 1.0, 0.0]]

for key, value in vars(args).items():
    log_param(key, value)

# #nproc = 8
# 
# # !pip install mlflow
# 
# import numpy
# rng = numpy.random.RandomState(seed)
# 
# import scopyon
# 
# config = scopyon.DefaultConfiguration()
# config.default.effects.photo_bleaching.switch = False
# config.default.detector.exposure_time = exposure_time
# pixel_length = config.default.detector.pixel_length / config.default.magnification
# L_2 = config.default.detector.image_size[0] * pixel_length * 0.5
# L_2
# 
# #config.environ.processes = nproc
# 
# timepoints = numpy.linspace(0, interval * num_frames, num_frames + 1)
# ndim = 2
# 
# import pathlib
# runid = run_obj.info.run_id
# artifactsPath = "/tmp/" + str(runid) + "/artifacts"
# artifacts = pathlib.Path(artifactsPath)
# artifacts.mkdir(parents=True, exist_ok=True)
# log_param("artifactsPath", artifactsPath)
# 
# config.save(artifacts / 'config.yaml')
# 
# for i in range(num_samples):
#     samples = scopyon.sample(timepoints, N=Nm, lower=-L_2, upper=+L_2, ndim=ndim, D=Dm, transmat=transmat, rng=rng)
#     inputs = [(t, numpy.hstack((points[:, : ndim], points[:, [ndim + 1]], numpy.ones((points.shape[0], 1), dtype=numpy.float64)))) for t, points in zip(timepoints, samples)]
#     ret = list(scopyon.generate_images(inputs, num_frames=num_frames, config=config, rng=rng, full_output=True))
#     
#     inputs_ = []
#     for t, data in inputs:
#         inputs_.extend(([t] + list(row) for row in data))
#     inputs_ = numpy.array(inputs_)
#     numpy.save(artifacts / f"inputs{i:03d}.npy", inputs_)
# 
#     numpy.save(artifacts / f"images{i:03d}.npy", numpy.array([img.as_array() for img, infodict in ret]))
# 
#     true_data = []
#     for t, (_, infodict) in zip(timepoints, ret):
#         true_data.extend([t, key] + list(value) for key, value in infodict['true_data'].items())
#     true_data = numpy.array(true_data)
#     numpy.save(artifacts / f"true_data{i:03d}.npy", true_data)
# 
# #!ls ./artifacts
# 
# log_artifacts(artifactsPath)

mlflow.end_run()
