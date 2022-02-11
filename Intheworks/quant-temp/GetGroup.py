
import yaml
import os

class GetGroup(object):
  yaml_file_path = os.path.join(os.path.dirname(__file__),'group')

  @staticmethod
  def get(index:str)->list:
    with open(os.path.join(GetGroup.yaml_file_path, '%s.yaml'%index)) as f:
      conf = yaml.load(f, Loader=yaml.FullLoader)
      ret = conf['stock'].values()
    return list(ret)

if __name__ == '__main__':
  c = GetGroup.get('apple-oled')
  print(c)