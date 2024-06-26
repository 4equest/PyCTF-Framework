import pickle
import utils
from .workspace import WorkSpace

def create_workspace(workspace_name: str) -> WorkSpace:
    """
    WorkSpaceの新規作成

    Args:
        workspace_name (str): WorkSpace名(重複可能)

    Returns:
        WorkSpace: WorkSpace
    """
    return WorkSpace(workspace_name=workspace_name)

def load_workspace(workspace_path: str) -> WorkSpace:
    """
    json形式のworkspaceを読み込む

    Args:
        workspace_path (str): _description_

    Returns:
        WorkSpace: WorkSpace
    """
    pass

def save_workspace(workspace: WorkSpace,workspace_path: str) -> int:
    """
    json形式のworkspaceを保存する
    モジュールなどの内部状態は破棄され結果のみが残る

    Args:
        workspace_path (str): WorkSpaceファイルパス

    Returns:
        int: 未定
    """
    pass

def load_workspace_unsafe(workspace_path: str) -> WorkSpace:
    """
    Pickleを用いたWorkspaceの読み込み
    信頼できないソースからのWorkspaceを開かないでください。

    Args:
        workspace_name (str): _description_

    Returns:
        WorkSpace: _description_
    """
    with open(workspace_path, "rb") as f:
        return pickle.load(f)
    

def save_workspace_unsafe(workspace: WorkSpace, workspace_path: str) -> int:
    """
    Pickleを用いたWorkspaceの保存
    モジュールの状態なども含めて保存できる

    Args:
        workspace_path (str): _description_

    Returns:
        int: 未定
    """
    with open(workspace_path, "wb") as f:
        pickle.dump(workspace, f)

    return 0