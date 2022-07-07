# -------------------------------------------------------------------
# this code runs cmaes first, then stop and study the log with tf
# then continue the optimization with the trained tf model
# ##########################################
# # V IS 105. SMALLER MODEL THAN V 3000    #
# ##########################################
# -------------------------------------------------------------------

# ------------------------------------------------
# Import
# ------------------------------------------------
import numpy as np
import tensorflow as tf
import os
import optuna
import sys
import time

tf.config.run_functions_eagerly(True)
# tf.enable_eager_execution()
# np.set_printoptions(threshold=sys.maxsize)
# os.environ['CUDA_VISIBLE_DEVICES'] = ''
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# gpu_options = tf.GPUOptions(allow_growth=True)

# -------------------------------------------------------------------
# constant
# -------------------------------------------------------------------


def make_pro_dic(path, key):
    mask_dict = {}
    for files in os.listdir(path):
        if "npz" in files:
            protname = files.split(".")[0]
            arrz = np.load(f"{path}{files}", allow_pickle=True)
            mask_dict[protname] = arrz[key]
    return mask_dict


########################################################################
# transformer
# variables to consider
########################################################################
# BASE_PATH = "/Users/mac/Desktop/t3_mnt/transformer_tape_dnabert/"
BASE_PATH = "/gs/hs0/tga-science/kimura/transformer_tape_dnabert/"
PROTEIN_SEQ_FILE = f"{BASE_PATH}data/protein128/"  # AARS.npy
protein_seq_dict_padded = make_pro_dic(PROTEIN_SEQ_FILE, "padded_array")
protein_seq_dict_unpadded = make_pro_dic(PROTEIN_SEQ_FILE, "unpadded_array")
cross_mask_dict = make_pro_dic(PROTEIN_SEQ_FILE, "cross_mask")
cross_mask_small_dict = make_pro_dic(PROTEIN_SEQ_FILE, "cross_mask_small")
RNA_SEQ_FILE = f"{BASE_PATH}data/RNA128_training_200/"  # 0.npy
WARMUP_STEPS = 5
USE_CHECKPOINT = True
# MAX_BATCH_NUM = 1700
MAX_EPOCHS = 10000
# MAX_BATCH_NUM = 10000
# NUM_LAYERS = 4
D_MODEL = 128
# NUM_HEADS = 8
DFF = 105
DROPOUT_RATE = 0.1
PROTNAMES = ['U2AF2', 'EIF3D', 'XPO5', 'LIN28B', 'TNRC6A', 'SF3B4', 'PABPN1', 'FAM120A', 'STAU2', 'AKAP8L', 'PCBP2', 'DDX51', 'CPSF6', 'FXR1', 'RPS11', 'UTP3', 'MATR3', 'FASTKD2', 'TROVE2', 'UTP18', 'KHSRP', 'AQR', 'IGF2BP1', 'DDX52', 'BCCIP', 'DDX42', 'EIF4G2', 'SAFB2', 'RPS5', 'PRPF4', 'UCHL5', 'SSB', 'SLTM', 'SND1', 'PCBP1', 'WDR43', 'TIAL1', 'RBM22', 'ZC3H8', 'DHX30', 'HNRNPUL1', 'FMR1', 'ILF3', 'SRSF7', 'SRSF1', 'PUM2', 'GEMIN5', 'TAF15', 'DDX21', 'FUS', 'SFPQ', 'APOBEC3C', 'UPF1', 'HNRNPL', 'YBX3', 'PUM1', 'KHDRBS1', 'PRPF8', 'POLR2G', 'SUB1', 'GPKOW', 'LARP4', 'PPIL4', 'SRSF9', 'FTO', 'SLBP', 'ABCF1', 'QKI', 'YWHAG', 'EIF3H', 'FUBP3', 'SUPV3L1', 'SBDS', 'HNRNPA1', 'DDX59', 'GTF2F1', 'WRN', 'HNRNPC', 'AARS', 'EFTUD2', 'XRN2', 'PHF6', 'NCBP2', 'NSUN2', 'SF3A3', 'NKRF', 'SERBP1', 'GRSF1', 'NOL12', 'EWSR1', 'ZNF622', 'EXOSC5', 'TRA2A', 'NOLC1', 'TARDBP', 'NONO', 'HNRNPU', 'AATF', 'DDX24', 'HNRNPM', 'DDX6', 'FKBP4', 'AKAP1', 'ZC3H11A', 'CDC40', 'NIP7', 'CPEB4', 'AGGF1', 'METAP2', 'BUD13', 'WDR3', 'TIA1', 'CSTF2T', 'SMNDC1', 'DDX3X', 'DGCR8', 'NIPBL', 'U2AF1', 'CSTF2', 'SUGP2', 'PABPC4', 'RPS3', 'PUS1', 'SAFB', 'IGF2BP3', 'ZRANB2', 'SDAD1', 'HLTF', 'EIF3G', 'ZNF800', 'RBFOX2', 'IGF2BP2', 'GRWD1', 'DDX55', 'G3BP1', 'RBM15', 'TBRG4', 'SF3B1', 'FXR2', 'LSM11', 'DKC1', 'BCLAF1', 'PTBP1', 'GNL3', 'RBM5', 'DROSHA', 'MTPAP', 'HNRNPK', 'LARP7', 'NPM1', 'PPIG', 'XRCC6']
final_target_vocab_size = 2
########################################################################
########################################################################

# BASE_PATH = "/gs/hs0/tga-science/kimura/BBO6_sepCMA/"
# quadrutic functin
SIGMA = 1

# TRAINING
TOTAL_SEEDS_IN_CMA_POP = np.arange(1, 2)  # seed for sampling
SEEDF_MAX = np.arange(0, 1)  # determines the shape of the target function
MAX_GENERATION = 99000

# how to make a training data
SKIP = 0
MEAN_SKIP = 1
LINE_TO_STOP_READ_DATA = None

# how to train
RUN_TRANINIG = True
# RUN_TRANINIG = True
EPOCH_TRAIN = 100
FILE_NUM_TRAIN = 10  # constant, dont change this! defined quadrutic function for data generation
BATCH_NUM = 100  # not using this any more
input_vocab_size = 3000  # looks important but no
target_vocab_size = 3000  # looks important but no

# predict
TARGET_FUNCTION_SEED = 1
PRED_MAX = 5000
PRED_FROM_EPOCH = 1  # From when the prediction starts, from scratch? continue?
SOS = tf.constant([[10] * 768], dtype="float16")
EOS = tf.constant([[11] * 768], dtype="float16")
path = BASE_PATH


class Tfconfig():
    def __init__(self):
        self.num_layers = None
        self.d_model = D_MODEL
        self.num_heads = None
        self.dff = DFF
        self.dropout_rate = DROPOUT_RATE
        self.file_num_to_train = FILE_NUM_TRAIN
        self.group_to_ignore = None
        self.max_epoch = MAX_EPOCHS
        self.max_batch_num = None
        self.datapath = None
        self.files_per_batch = 1
        self.init_lr = None

    def update(self):
        self.taskname = f"protein_{self.group_to_ignore}_{self.max_batch_num}files_128_lr{self.init_lr}_correct105"
        self.checkpoint_path = f"{BASE_PATH}_{self.taskname}"
        self.ignorelist = PROTNAMES[self.group_to_ignore * 38:(self.group_to_ignore + 1) * 38]
        self.protlist = [x for x in PROTNAMES if x not in self.ignorelist]


# ------------------------------------------------
# Functions
# ------------------------------------------------


def print_and_time(name, ut):
    tf.print(f"{name} done {time.time() - ut}")
    ut = time.time()
    return ut


def get_protein_seq(protname):
    arr = np.load(f"{path}{protname}.npy")
    return arr


def is_pos_def(A):
    M = np.matrix(A)
    return np.all(np.linalg.eigvals(M + M.transpose()) > 0)


def get_list_fromlog(keyword, logfile):
    targetlist = []
    with open(logfile) as f:
        for lines in f.readlines():
            if keyword == lines[:len(keyword)]:
                str_list = lines.replace(keyword, "").replace("\n", "").split(",")
                list_to_add = [float(x) for x in str_list]
                targetlist.append(list_to_add)
    return targetlist


def write_all(mean_list, logpath, iternum, q_and_r_list, cov_mat):
    with open(logpath.replace(".csv", "_only_iternum.csv"), "a") as f:
        f.writelines(str(iternum) + "\n")

    with open(logpath, "a") as f:
        # write query and response
        f.writelines(f"{iternum}:q_and_r:")
        f.write(",".join(str(x) for x in q_and_r_list))
        f.writelines("\n")

        # write mean
        f.writelines(f"{iternum}:mean:")
        f.write(",".join(str(x) for x in mean_list))
        f.writelines("\n")

        # write matrix
        # row_count = 0
        f.writelines(f"{iternum}:cov:")
        f.write(",".join(str(x) for x in cov_mat))
        f.writelines("\n")


def iter_num_not_yet(num, logfile):
    with open(logfile.replace(".csv", "_only_iternum.csv")) as f:
        # line_list = f.readlines()
        try:
            lastline = f.readlines()[-1]
            return lastline == str(num) + "\n"
        except IndexError:
            print(num)


def reset_log(file_path):
    with open(file_path, "w"):
        pass
    with open(file_path.replace(".csv", "_only_iternum.csv"), "w"):
        pass


sos = SOS
eos = EOS


def create_tar_padding_mask(seq):
    seq = tf.cast(tf.math.equal(seq, 0), tf.float16)
    return seq[:, tf.newaxis, tf.newaxis, :]  # (batch_size, 1, 1, seq_len)


def scaled_dot_product_attention(k, q, v, mask, location, smask=None, block_num=None):  # q, k, v, mask, mha_num, smask
    matmul_qk = tf.cast(tf.matmul(q, k, transpose_b=True), tf.float32)  # (..., seq_len_q, seq_len_k)
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    if smask is not None:  # decoder
        if block_num == 0:
            mask = tf.cast(mask, tf.float32)
        else:
            mask = tf.cast(smask, tf.float32)
    else:  # encoder
        mask = tf.cast(mask, tf.float32)
    v = tf.cast(v, tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)  # (1, 34, 29, 29)
    if mask is not None:
        scaled_attention_logits += (mask * -1e9)
    attention_weights = tf.cast(tf.nn.softmax(scaled_attention_logits, axis=-1), tf.float32)  # (..., seq_len_q, seq_len_k)
    if location == 3:  # Encoder
        output = tf.matmul(tf.transpose(attention_weights, perm=[0, 1, 3, 2]), v)  # (..., seq_len_q, depth_v)
    else:  # Decoder
        output = tf.matmul(tf.transpose(attention_weights, perm=[0, 1, 3, 2]), v)  # (..., seq_len_q, depth_v)
    return output, attention_weights


def point_wise_feed_forward_network(d_model, dff):
    return tf.keras.Sequential([
        tf.keras.layers.Dense(dff, activation='relu'),  # (batch_size, seq_len, dff)
        tf.keras.layers.Dense(d_model)  # (batch_size, seq_len, d_model)
    ])


class FinalLayer(tf.keras.layers.Layer):
    def __init__(self):
        super(FinalLayer, self).__init__()
        self.finallayer = tf.keras.layers.Dense(final_target_vocab_size)

    def call(self, x):  # x is a 2d vector
        # normalize
        logits = tf.math.l2_normalize(self.finallayer(x))  # [[-0.953382075 0.301765621]]
        # softmax
        # finalvalue = tf.nn.softmax(logits, axis=-1)
        # return finalvalue
        return logits


class Transformer(tf.keras.Model):
    def __init__(self, num_layers, d_model, num_heads, dff, input_vocab_size,
                 target_vocab_size, pe_input, pe_target, rate=0.1):
        super(Transformer, self).__init__()
        self.encoder = Encoder(num_layers, d_model, num_heads, dff,
                               input_vocab_size, pe_input, rate)
        self.decoder = Decoder(num_layers, d_model, num_heads, dff,
                               target_vocab_size, pe_target, rate)
        self.final_layer = FinalLayer()

    def call(self, inp, tar, training, enc_padding_mask, cross_padding_mask_small, cross_padding_mask):
        inp = tf.cast(inp, tf.float16)
        enc_output = self.encoder(inp, training, enc_padding_mask)  # (batch_size, inp_seq_len, d_model)
        dec_output, attention_weights = self.decoder(tar, enc_output, training, cross_padding_mask, cross_padding_mask_small)
        final_output = self.final_layer(tf.reduce_sum(dec_output, axis=-2))  # output: 1-dimensional values
        return final_output, attention_weights


class MultiHeadAttention(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        assert d_model % self.num_heads == 0
        self.depth = d_model // self.num_heads  # depth = 128 /4 = 32
        self.wq = tf.keras.layers.Dense(d_model)
        self.wk = tf.keras.layers.Dense(d_model)
        self.wk2 = tf.keras.layers.Dense(d_model)
        self.wv = tf.keras.layers.Dense(d_model)
        self.dense = tf.keras.layers.Dense(d_model)

    def split_heads(self, x, batch_size):
        """Split the last dimension into (num_heads, depth).
        Transpose the result such that the shape is (batch_size, num_heads, seq_len, depth)
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, v, q, k, mask, training, block_num=None, mha_num=None, smask=None):
        batch_size = tf.shape(q)[0] #  mha_num 2 : Dec layer, mha_num 3 : Enc layer
        v = self.wv(v)
        k = self.wk(k)
        q = self.wq(q)
        # split
        q = self.split_heads(q, batch_size)  # (batch_size, num_heads, seq_len_q, depth)
        k = self.split_heads(k, batch_size)  # (batch_size, num_heads, seq_len_k, depth)
        v = self.split_heads(v, batch_size)  # (batch_size, num_heads, seq_len_v, depth)
        # calc. attention
        scaled_attention, attention_weights = scaled_dot_product_attention(
            q, k, v, mask, mha_num, smask, block_num)
        scaled_attention = tf.transpose(scaled_attention,
                                        perm=[0, 2, 1, 3])  # (batch_size, seq_len_q, num_heads, depth)
        concat_attention = tf.reshape(scaled_attention,
                                      (batch_size, -1, self.d_model))  # (batch_size, seq_len_q, d_model)
        output = self.dense(concat_attention)  # (batch_size, seq_len_q, d_model)
        return output, attention_weights


class EncoderLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dff, rate=0.1):
        super(EncoderLayer, self).__init__()
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = point_wise_feed_forward_network(d_model, dff)
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)
    def call(self, x, training, mask, block_num=None):
        attn_output, _ = self.mha(x, x, x, mask, training, block_num, 3)  # (batch_size, input_seq_len, d_model)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)  # (batch_size, input_seq_len, d_model)
        ffn_output = self.ffn(out1)  # (batch_size, input_seq_len, d_model)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)  # (batch_size, input_seq_len, d_model)
        return out2


class DecoderLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dff, rate=0.1):
        super(DecoderLayer, self).__init__()
        self.mha1 = MultiHeadAttention(d_model, num_heads)
        self.mha2 = MultiHeadAttention(d_model, num_heads)
        self.ffn = point_wise_feed_forward_network(d_model, dff)
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)
        self.dropout3 = tf.keras.layers.Dropout(rate)
    def call(self, x, enc_output, training,  # x:RNA, enc_output:protein
             cross_padding_mask, block_num=None, cross_mask_small=None):
        out1 = x
        #                                       v,          q,      k
        attn2, attn_weights_block2 = self.mha2(out1, enc_output, out1, cross_padding_mask, training, block_num, 2, cross_mask_small)
        attn2 = self.dropout2(attn2, training=training)  # (49, 105, 768)
        if block_num == 0:
            out2 = attn2
        else:
            out2 = self.layernorm2(attn2 + out1)  # (batch_size, target_seq_len, d_model)
        ffn_output = self.ffn(out2)  # (batch_size, target_seq_len, d_model)
        ffn_output = self.dropout3(ffn_output, training=training)
        out3 = self.layernorm3(ffn_output + out2)  # (batch_size, target_seq_len, d_model)
        # return out3, attn_weights_block1, attn_weights_block2
        return out3, attn_weights_block2


class Encoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, input_vocab_size,
                 maximum_position_encoding, rate=0.1):
        super(Encoder, self).__init__()
        self.d_model = tf.cast(d_model, tf.float16)
        self.num_layers = num_layers
        self.enc_layers = [EncoderLayer(d_model, num_heads, dff, rate)
                           for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)

    def call(self, x, training, mask):
        x = self.dropout(x, training=training)
        x = tf.cast(x, tf.float16)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float16))
        x /= tf.cast(self.d_model, tf.float16)
        for i in range(self.num_layers):
            x = self.enc_layers[i](x, training, mask, i)
        return x  # (batch_size, input_seq_len, d_model)


class Decoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, target_vocab_size,
                 maximum_position_encoding, rate=0.1):
        super(Decoder, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers
        self.dec_layers = [DecoderLayer(d_model, num_heads, dff, rate)
                           for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)

    def call(self, x, enc_output, training, cross_padding_mask, cross_padding_mask_small):  # x = tar previously
        attention_weights = {}
        x = tf.cast(x, tf.float16)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float16))
        x /= tf.cast(self.d_model, tf.float16)
        x = self.dropout(x, training=training)
        for i in range(self.num_layers):
            # def call(self, x, enc_output, training,  # x:RNA, enc_output:protein
            #          pro_padding_mask, cross_padding_mask, wordlen=None,
            #          block_num=None):  # tar, enc_output, training, look_ahead_mask, dec_padding_mask)
            x, block1 = self.dec_layers[i](x, enc_output, training, cross_padding_mask, i, cross_padding_mask_small)
            attention_weights['decoder_layer{}_block1'.format(i + 1)] = block1

        return x, attention_weights


class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, d_model, warmup_steps=WARMUP_STEPS):
        super(CustomSchedule, self).__init__()
        self.d_model = d_model
        self.d_model = tf.cast(self.d_model, tf.float16)
        self.warmup_steps = warmup_steps

    def __call__(self, step):
        arg1 = tf.math.rsqrt(step)
        arg2 = step * (self.warmup_steps ** -1.5)
        return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)


class CustomSchedule2(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, d_model, warmup_steps=WARMUP_STEPS):
        super(CustomSchedule2, self).__init__()

    def __call__(self, step):
        rate = 2 ** (-step * 10)
        return rate


def opt_trfmr(tfconfig):

    # ------------------------------------------------
    # Constant
    # ------------------------------------------------
    use_checkpoint = USE_CHECKPOINT
    num_layers = tfconfig.num_layers
    d_model = tfconfig.d_model
    dff = tfconfig.dff
    num_heads = tfconfig.num_heads
    dropout_rate = tfconfig.dropout_rate

    max_epoch = tfconfig.max_epoch
    checkpoint_path = tfconfig.checkpoint_path
    if not os.path.isdir(checkpoint_path):
        os.mkdir(checkpoint_path)
    # if not os.path.isfile(logfile):
    #     with open(logfile, "w") as f:
    #         pass

    # loss_object = tf.keras.losses.MeanAbsoluteError(reduction=tf.keras.losses.Reduction.SUM)
    # loss_object = tf.keras.losses.MeanSquaredError(reduction=tf.keras.losses.Reduction.SUM_OVER_BATCH_SIZE)

    # ------------------------------------------------
    # Class & Function
    # ------------------------------------------------


    def accuracy_function(labellist, predictions):
        predicted_labels = tf.math.greater_equal(predictions, tf.constant(0.5))
        predicted_labels = tf.cast(predicted_labels, dtype="float16")
        labellist = tf.reshape(labellist, [labellist.shape[0]])
        accuracies = tf.math.equal(predicted_labels, labellist)
        accuracies = tf.cast(accuracies, dtype="float16")
        return tf.reduce_sum(accuracies) / tf.constant(200, dtype="float16")
        # accuracies = tf.equal(real, tf.argmax(pred, axis=2))
        # mask = tf.math.logical_not(tf.math.equal(real, 0))
        # accuracies = tf.math.logical_and(mask, accuracies)
        # accuracies = tf.cast(accuracies, dtype=tf.float32)
        # mask = tf.cast(mask, dtype=tf.float32)
        # return tf.reduce_sum(accuracies) / tf.reduce_sum(mask)


    def loss_function(labellist, predictions):
        new_labellist = [[1, 0] if x == 0 else [0, 1] for x in labellist]
        # for item in labellist:
        #     if item == 0:
        #         label = [1, 0]
        #     else:
        #         label = [0, 1]
        #     new_labellist.append(label)
        # bce = tf.keras.losses.BinaryCrossentropy(from_logits=False)
        bce = tf.nn.softmax_cross_entropy_with_logits(new_labellist, predictions, axis=-1)
        lossvalue = tf.cast(bce, dtype="float16")
        return lossvalue


    ###############################################
    # 1. read files to 3 lists
    ###############################################
    input_list_list, label_list_list = [], []
    """## **ここからがメイン。**"""

    transformer = Transformer(num_layers, d_model, num_heads, dff,
                              input_vocab_size, target_vocab_size,
                              pe_input=input_vocab_size,
                              pe_target=target_vocab_size,
                              rate=dropout_rate)

    learning_rate = CustomSchedule(d_model)

    optimizer = tf.keras.optimizers.Adam(tfconfig.init_lr, beta_1=0.9, beta_2=0.9999,
                                         epsilon=1e-6)
    # optimizer = tf.keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98,
    #                                      epsilon=1e-9)
    # optimizer = tf.keras.optimizers.Adam(0.01, beta_1=0.9, beta_2=0.98,
    #                                      epsilon=1e-2, amsgrad=True)
    # optimizer = tf.keras.optimizers.Nadam()
    # optimizer = tf.keras.optimizers.SGD()

    # optimizer = tf.keras.optimizers.Adadelta(learning_rate, rho=0.95,
    #                                          epsilon=1e-07, name='Adadelta')

    # ----------------------------
    # check point
    # ----------------------------
    ckpt = tf.train.Checkpoint(transformer=transformer,
                               optimizer=optimizer)
    ckpt_manager = tf.train.CheckpointManager(ckpt, checkpoint_path, max_to_keep=5)

    if use_checkpoint:
        if ckpt_manager.latest_checkpoint:
            ckpt.restore(ckpt_manager.latest_checkpoint)
            # with open(logtest, 'a') as f:
            #     tf.print('Latest checkpoint restored!!')
            #     f.writelines('Latest checkpoint restored!!')


    # get #1 protein vecs, #2 rna_vecs, #3 rna padding, #4 protein padding, #5 cross padding
    def get_three_veclists(inp):  # inp = [proid_array, feat_array, label_array]
        protein_name_list = [PROTNAMES[abs(int(x))] for x in inp[0]]
        pvecs_list_padded = np.array([protein_seq_dict_padded[x] for x in protein_name_list])  # previously np.array
        pvecs_list_unpadded = np.array([protein_seq_dict_unpadded[x][0] for x in protein_name_list])
        pro_padding_mask_list = [np.concatenate([[0] * x.shape[0], [1] * (3000 - x.shape[0])]) for x in pvecs_list_unpadded]
        r_padding_mask = np.concatenate([[0]*102, [1]*3])

        cross_padding_mask_list = np.array([cross_mask_dict[x] for x in protein_name_list])
        cross_padding_mask_list_small = np.array([cross_mask_small_dict[x] for x in protein_name_list])

        rna_padding_mask_list = np.array([r_padding_mask] * len(inp[0]))

        rna_vec_list = inp[1]
        rna_vec_list = tf.convert_to_tensor(rna_vec_list, dtype=tf.float16)
        label_list = inp[2]
        label_list = tf.convert_to_tensor(label_list, dtype=tf.float16)
        cross_padding_mask_list = tf.cast(cross_padding_mask_list, dtype="float16")
        cross_padding_mask_list = cross_padding_mask_list[:, tf.newaxis, :, :]
        cross_padding_mask_list_small = tf.cast(cross_padding_mask_list_small, dtype="float16")
        cross_padding_mask_list_small = cross_padding_mask_list_small[:, tf.newaxis, :, :]
        pro_padding_mask_list = tf.cast(pro_padding_mask_list, dtype="float16")
        pro_padding_mask_list = pro_padding_mask_list[0:1, tf.newaxis, tf.newaxis, :]
        rna_padding_mask_list = tf.cast(rna_padding_mask_list, dtype="float16")
        rna_padding_mask_list = rna_padding_mask_list[0:1, tf.newaxis, tf.newaxis, :]
        return [pvecs_list_padded, rna_vec_list, label_list, pro_padding_mask_list, rna_padding_mask_list, cross_padding_mask_list, cross_padding_mask_list_small]


    # @tf.function(input_signature=train_step_signature)
    @tf.function()
    def train_step(inp, m):  # tar : (100, 30, 170)
        # get protein seqs, and make masks
        tar_inp, inp, labellist, pro_padding, rna_padding, cross_mask, cross_mask_small = get_three_veclists(inp)  # protein features vecs
        if tar_inp is None:
            return [None, m]
        enc_padding_mask = rna_padding
        dec_padding_mask = pro_padding
        # enc_padding_mask, combined_mask, dec_padding_mask = create_masks_auth(inp, tar_inp, pro_effective_vec_len_list)
        with tf.GradientTape() as tape:
            predictions, _ = transformer(inp, tar_inp,  # "call" is called here
                                                     True,
                                                     enc_padding_mask,
                                                     cross_mask_small,
                                                     cross_mask)
            loss = loss_function(labellist, predictions)
        accuracy = accuracy_function(labellist, tf.nn.softmax(predictions)[:, 1])
        # if prediction is [0.23, 0.77] and the label is 1, 0.77 is compared to 1
        m.update_state(labellist, tf.nn.softmax(predictions)[:, 1].numpy())
        gradients = tape.gradient(loss, transformer.trainable_variables)
        optimizer.apply_gradients(zip(gradients, transformer.trainable_variables))
        return loss, m, accuracy


    # make instances for evaluating optimization
    batch_loss = tf.keras.metrics.Mean(name='train_loss')
    epoch_accuracy = tf.keras.metrics.Mean(name='train_accuracy')
    auc = tf.keras.metrics.AUC()

    for epoch in range(max_epoch):
        # 1 EPOCH
        auc.reset_states()
        epoch_accuracy.reset_states()

        for batch_count in range(tfconfig.max_batch_num):
            # 1 BATCH
            # batch_loss.reset_states()
            # for i in range(tfconfig.files_per_batch):
            npz_to_add = np.load(f"{tfconfig.datapath}{batch_count}.npz", allow_pickle=True)
            # npz_to_add = np.load(f"{tfconfig.datapath}{tfconfig.files_per_batch * batch_count + i}.npz", allow_pickle=True)
                # if i == 0:
                    # padded_array=padded_array, unpadded_array=new_array,
                    # cross_mask=cross_mask_array, cross_mask_small=cross_mask_array_small)
            # proid_array = npz_to_add["proid"]
            # feat_array = npz_to_add["feature"]
            # label_array = npz_to_add["label"]
                # else:
                #     proid_array = np.concatenate((proid_array, npz_to_add["proid"]))  # (50, 3,)
                #     feat_array = np.concatenate((feat_array, npz_to_add["feature"]))  # (50, 3,)
                #     label_array = np.concatenate((label_array, npz_to_add["label"]))  # (50, 3,)
            train_array = [npz_to_add["proid"], npz_to_add["feature"], npz_to_add["label"]]
            loss, auc, accuracy = train_step(train_array, auc)
            if loss is None:
                continue
            # batch_loss(loss)
            epoch_accuracy.update_state(accuracy)
            if batch_count % 10 == 0:
                ckpt_manager.save()
        # return float(auc.result().numpy())
        tf.print(f"EPOCH:{epoch} AUROC:{auc.result().numpy()} ACCURACY:{epoch_accuracy.result().numpy()}")


# -------------------------------------------------------------------
# main
# -------------------------------------------------------------------
if __name__ == '__main__':
    tfconfig = Tfconfig()
    tfconfig.init_lr = 10 ** (- int(sys.argv[2]))
    tfconfig.num_layers = 3
    tfconfig.num_heads = 4
    tfconfig.max_batch_num = 1700  # 1 epoch data size = 10 * files_per_batch * max_batch_num
    tfconfig.group_to_ignore = int(sys.argv[1])
    tfconfig.files_per_batch = 1
    tfconfig.datapath = f"{RNA_SEQ_FILE}{tfconfig.group_to_ignore}/"
    tfconfig.update()
    opt_trfmr(tfconfig)
