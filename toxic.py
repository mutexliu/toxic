import data_source
import model
import log
import train
import infer

log_dir = log.init_log()

embed_file = 'data/crawl-300d-2M.vec'

toxic_data = data_source.FastData(seq_length=320)
# toxic_data = data_source.DataSource(embed_file, embed_dim=300)

print(toxic_data.description())

train_model = model.AttenModel(toxic_data)

train_fold = True

if train_fold:
    result_model = train.train_folds(train_model, 10, log_dir)
else:
    result_model = train.train(train_model, log_dir)
print('train finish', 'result_model: ', result_model)
result_file = train_model.description + '.csv'
infer.infer_result(result_model, toxic_data, log_dir, result_file)
