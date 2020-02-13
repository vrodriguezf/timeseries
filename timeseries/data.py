# AUTOGENERATED! DO NOT EDIT! File to edit: 80_timeseries_data.ipynb (unless otherwise specified).

__all__ = ['TSData', 'get_ts_items', 'show_timeseries', 'download_unzip_data', 'unzip', 'download_unzip_data_UCR',
           'get_UCR_univariate_list', 'get_UCR_multivariate_list']

# Cell
from fastai2.torch_basics import *
from fastai2.data.all import *

# Cell
from zipfile import ZipFile

# Cell
class TSData():
    "Class that loads .arff (soon .ts) files and returns a tuple (self.x , self.y)"
    "self.x is a list of 2D array with a shape (n_samples, nb_channels, sequence_length) "
    "self.y is a 1D array as y (i.e. label) with a shape (n_samples)"
    "for the NATOPS_Train.arff file, the result will be : x(180, 24, 51) and y(180)"
    def __init__(self):
        self.x = self.y = self.dsname = self.fnames = []

    # def __init__(self, fnames, has_targets=True, fill_missing='NaN'):
    #     self.x = self.y = self.dsname = []
    #     self.fnames = fnames
    #     self.has_targets = has_targets
    #     self.fill_missings = fill_missing
    #     # load(fnames, has_targets=has_targets, fill_missing=fill_missing)



    def __repr__(self): return f"{self.__class__.__name__}:\n Datasets names (concatenated): {self.dsname}\n Filenames: \                   {self.fnames}\n Data shape: {self.x.shape}\n Targets shape: {self.y.shape}\n Nb Samples: {self.x.shape[0]}\n Nb Channels: \         {self.x.shape[1]}\n Sequence Length: {self.x.shape[2]}"

    def get_x(self, as_list=True): return(list(self.x))
    def get_y(self): return(self.y)
    def get_items(self): return [(item, label) for (item, label) in zip(list(self.x), self.y)]
    def __getitem__(self, i): return (self.x[i], self.y[i])

    @classmethod
    def get_ts_items(self, fnames, has_targets=True, fill_missing='NaN'):
        (self.x, self.y) = load(fnames, has_targets, fill_missing)


    @property
    def sizes(self): return (self.x.shape, self.y.shape)

    @property
    def n_channels(self): return (self.x.shape[1])

    def _load(self, fname, has_targets=True, fill_missing='NaN'):
        "load an .arff file and return a tupple of 2 numpy arrays: "
        "x : array with a shape (n_samples, nb_channels, sequence_length)"
        "y : array with a shape (n_samples)"
        "for the NATOPS_Train.arff  the result will be : x(180, 24, 51) and y(180)"

        instance_list = []
        class_val_list = []
        data_started = False
        is_multi_variate = False
        is_first_case = True

        with open(fname, 'r') as f:
            for line in f:
                if line.strip():
                    if is_multi_variate is False and "@attribute" in line.lower() and "relational" in line.lower():
                        is_multi_variate = True
                    if "@data" in line.lower():
                        data_started = True
                        continue
                    # if the 'data tag has been found, the header information has been cleared and now data can be loaded
                    if data_started:
                        line = line.replace("?", fill_missing)
                        if is_multi_variate:
                            if has_targets:
                                line, class_val = line.split("',")
                                class_val_list.append(class_val.strip())
                            dimensions = line.split("\\n")
                            dimensions[0] = dimensions[0].replace("'", "")

                            if is_first_case:
                                for d in range(len(dimensions)):
                                    instance_list.append([])
                                is_first_case = False

                            for dim in range(len(dimensions)):
                                instance_list[dim].append(np.array(dimensions[dim].split(','), dtype=np.float32))
#                                 instance_list[dim].append(np.fromiter(dimensions[dim].split(','), dtype=np.float32))
                        else:
                            if is_first_case:
                                instance_list.append([])
                                is_first_case = False

                            line_parts = line.split(",")

                            if has_targets:
                                instance_list[0].append(np.array(line_parts[:len(line_parts)-1], dtype=np.float32))

                                class_val_list.append(line_parts[-1].strip())
                            else:
                                instance_list[0].append(np.array(line_parts[:len(line_parts)-1], dtype=np.float32))

        #instance_list has a shape of (dimensions, nb_samples, seq_lenght)
        #for the NATOPS_Train.arff it would be (24, 180, 51)
        #convert python list to numpy array and transpose the 2 first dimensions -> (180, 24, 51)
        x = np.asarray(instance_list).transpose(1,0,2)

        if has_targets:
            y = np.asarray(class_val_list)
            return x, y
        else:
            return x, [None*x.shape[0]]

    def load(self, fnames, has_targets=True, fill_missing='NaN'):
        if isinstance(fnames, list):
            self.x = []
            self.y = []
            self.dsname = []
            self.fnames = []
            xs,ys = [],[]
            for i, fn in enumerate(fnames):
                x,y = self._load(fn, has_targets=has_targets, fill_missing=fill_missing)
                xs.append(x)
                ys.append(y)
                self.fnames.append(fn)
                self.dsname.append(fn.stem)
            self.x = np.concatenate(xs)
            self.y = np.concatenate(ys)
        else:
            self.fnames.append(fnames)
            self.dsname.append(fnames.stem)
            self.x, self.y = self._load(fnames, has_targets=has_targets, fill_missing=fill_missing)

        return (self.x, self.y)




# Cell
def get_ts_items(fnames):
    data = TSData()
    data.load(fnames)
    return data.get_items()

# Cell
def show_timeseries(ts, ctx=None, title=None, chs=None, leg=True, **kwargs):
    r"""
    Plot a timeseries.

    Args:

        title : usually the class of the timeseries

        ts : timeseries. It should have a shape of (nb_channels, sequence_length)

        chs : array representing a list of channels to plot

        leg : Display or not a legend
    """

    if ctx is None: fig, ctx = plt.subplots()
    t = range(ts.shape[1])
    chs_max = max(chs) if chs else 0
    channels = chs if (chs and (chs_max < ts.shape[0])) else range(ts.shape[0])
    for ch in channels:
        ctx.plot(t, ts[ch], label='ch'+str(ch))
    if leg: ctx.legend(loc='upper right', ncol=2, framealpha=0.5)
    if title: ctx.set_title(title)
    return ctx

# Cell
def download_unzip_data(url=None, path_data=None, dsname=None, c_key='archive', force_download=False):
    if url is None:
        print(f'Please enter a valid ${url} to a dataset to be downloaded')
        return None

    if dsname is None:
        print(f'Please enter a valid ${dsname} of the dataset name to be downloaded')
        return None


    "Download `url` to `path_data/dsname` folder."
    url_file = url + dsname + '.zip' #url_file = 'http://www.timeseriesclassification.com/Downloads/NATOPS.zip'
    dest_fname = path_data/f'{dsname}.zip'
    dest_dir = path_data/dsname # same name as the filename

    if not dest_fname.exists() or force_download:
        download_url(url_file, dest_fname, overwrite=force_download)
        unzip(dest_fname, dest_dir)
    return dest_dir

def unzip(dsname, dest_dir, verbose=False):
    with ZipFile(dsname, 'r') as zip:
        if verbose:
            zip.printdir()
            print(f'Extracting all the files from : {dsname}')
        zip.extractall(path=dest_dir)

def download_unzip_data_UCR(path_data=None, dsname=None, c_key='archive', force_download=False):
    url = 'http://www.timeseriesclassification.com/Downloads/'
    if path_data is None: path_data = Config().data

    return download_unzip_data(url=url, path_data=path_data, dsname=dsname, c_key=c_key, force_download=force_download)

# Cell
def get_UCR_univariate_list():
    return [
        'ACSF1', 'Adiac', 'AllGestureWiimoteX', 'AllGestureWiimoteY',
        'AllGestureWiimoteZ', 'ArrowHead', 'Beef', 'BeetleFly', 'BirdChicken',
        'BME', 'Car', 'CBF', 'Chinatown', 'ChlorineConcentration',
        'CinCECGtorso', 'Coffee', 'Computers', 'CricketX', 'CricketY',
        'CricketZ', 'Crop', 'DiatomSizeReduction',
        'DistalPhalanxOutlineAgeGroup', 'DistalPhalanxOutlineCorrect',
        'DistalPhalanxTW', 'DodgerLoopDay', 'DodgerLoopGame',
        'DodgerLoopWeekend', 'Earthquakes', 'ECG200', 'ECG5000', 'ECGFiveDays',
        'ElectricDevices', 'EOGHorizontalSignal', 'EOGVerticalSignal',
        'EthanolLevel', 'FaceAll', 'FaceFour', 'FacesUCR', 'FiftyWords',
        'Fish', 'FordA', 'FordB', 'FreezerRegularTrain', 'FreezerSmallTrain',
        'Fungi', 'GestureMidAirD1', 'GestureMidAirD2', 'GestureMidAirD3',
        'GesturePebbleZ1', 'GesturePebbleZ2', 'GunPoint', 'GunPointAgeSpan',
        'GunPointMaleVersusFemale', 'GunPointOldVersusYoung', 'Ham',
        'HandOutlines', 'Haptics', 'Herring', 'HouseTwenty', 'InlineSkate',
        'InsectEPGRegularTrain', 'InsectEPGSmallTrain', 'InsectWingbeatSound',
        'ItalyPowerDemand', 'LargeKitchenAppliances', 'Lightning2',
        'Lightning7', 'Mallat', 'Meat', 'MedicalImages', 'MelbournePedestrian',
        'MiddlePhalanxOutlineAgeGroup', 'MiddlePhalanxOutlineCorrect',
        'MiddlePhalanxTW', 'MixedShapes', 'MixedShapesSmallTrain',
        'MoteStrain', 'NonInvasiveFetalECGThorax1',
        'NonInvasiveFetalECGThorax2', 'OliveOil', 'OSULeaf',
        'PhalangesOutlinesCorrect', 'Phoneme', 'PickupGestureWiimoteZ',
        'PigAirwayPressure', 'PigArtPressure', 'PigCVP', 'PLAID', 'Plane',
        'PowerCons', 'ProximalPhalanxOutlineAgeGroup',
        'ProximalPhalanxOutlineCorrect', 'ProximalPhalanxTW',
        'RefrigerationDevices', 'Rock', 'ScreenType', 'SemgHandGenderCh2',
        'SemgHandMovementCh2', 'SemgHandSubjectCh2', 'ShakeGestureWiimoteZ',
        'ShapeletSim', 'ShapesAll', 'SmallKitchenAppliances', 'SmoothSubspace',
        'SonyAIBORobotSurface1', 'SonyAIBORobotSurface2', 'StarlightCurves',
        'Strawberry', 'SwedishLeaf', 'Symbols', 'SyntheticControl',
        'ToeSegmentation1', 'ToeSegmentation2', 'Trace', 'TwoLeadECG',
        'TwoPatterns', 'UMD', 'UWaveGestureLibraryAll', 'UWaveGestureLibraryX',
        'UWaveGestureLibraryY', 'UWaveGestureLibraryZ', 'Wafer', 'Wine',
        'WordSynonyms', 'Worms', 'WormsTwoClass', 'Yoga'
    ]

def get_UCR_multivariate_list():
    return [
        'ArticularyWordRecognition', 'AtrialFibrillation', 'BasicMotions',
        'CharacterTrajectories', 'Cricket', 'DuckDuckGeese', 'EigenWorms',
        'Epilepsy', 'EthanolConcentration', 'ERing', 'FaceDetection',
        'FingerMovements', 'HandMovementDirection', 'Handwriting', 'Heartbeat',
        'JapaneseVowels', 'Libras', 'LSST', 'InsectWingbeat', 'MotorImagery',
        'NATOPS', 'PenDigits', 'PEMS-SF', 'PhonemeSpectra', 'RacketSports',
        'SelfRegulationSCP1', 'SelfRegulationSCP2', 'SpokenArabicDigits',
        'StandWalkJump', 'UWaveGestureLibrary'
    ]