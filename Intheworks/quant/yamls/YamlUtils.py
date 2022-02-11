import yaml
import os

class YamlUtils:
  yaml_file_path = os.path.join(os.path.dirname(__file__))

  @staticmethod
  def get(index:str):
    with open(os.path.join(YamlUtils.yaml_file_path, '%s.yaml'%index.upper())) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
    return conf

if __name__ == '__main__':
  c = YamlUtils.get('per')
  print(c)
