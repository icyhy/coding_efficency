# -*- coding: utf-8 -*-
"""
仓库管理API模块
包含Git仓库的添加、管理、同步等功能
"""

from flask import request, current_app
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import requests
import json

from . import repository_bp as api_bp
from ..models import Repository, User, Commit, MergeRequest
from .. import db
from ..utils.response import (
    success_response, error_response, validation_error_response,
    not_found_response, conflict_response, created_response,
    updated_response, deleted_response, paginated_response
)
from ..utils.validators import validate_url, validate_git_url
from ..utils.auth import token_required, get_current_user
from ..utils.helpers import get_pagination_params, paginate_query
from ..utils.crypto import encrypt_data, decrypt_data

@api_bp.route('/', methods=['GET'])
@token_required
def get_repositories(current_user):
    """
    获取用户的仓库列表
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        page (int): 页码，默认为1
        per_page (int): 每页数量，默认为10
        platform (str): 平台筛选
        is_active (bool): 是否激活筛选
        search (str): 搜索关键词
    
    Returns:
        JSON响应包含分页的仓库列表
    """
    try:
        pagination_params = get_pagination_params()
        page = pagination_params['page']
        per_page = pagination_params['per_page']
        
        # 获取查询参数
        platform = request.args.get('platform')
        is_active = request.args.get('is_active')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = Repository.query.filter_by(user_id=current_user.id)
        
        # 平台筛选
        if platform:
            query = query.filter(Repository.platform == platform)
        
        # 激活状态筛选
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            query = query.filter(Repository.is_active == is_active_bool)
        
        # 搜索筛选
        if search:
            query = query.filter(
                Repository.name.contains(search) |
                Repository.url.contains(search)
            )
        
        # 排序
        query = query.order_by(Repository.created_at.desc())
        
        # 分页
        pagination_result = paginate_query(query, page, per_page)
        repositories = pagination_result['items']
        total = pagination_result['total']
        
        # 转换为字典格式
        repositories_data = []
        for repo in repositories:
            repo_data = repo.to_dict()
            # 添加统计信息
            repo_data['stats'] = {
                'commits_count': repo.get_commit_count(),
                'merge_requests_count': repo.get_merge_request_count()
            }
            repositories_data.append(repo_data)
        
        return paginated_response(
            items=repositories_data,
            page=page,
            per_page=per_page,
            total=total,
            message="获取仓库列表成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取仓库列表失败: {str(e)}")
        return error_response("获取仓库列表失败")

@api_bp.route('/', methods=['POST'])
@token_required
def create_repository(current_user):
    """
    添加新仓库
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "name": "仓库名称",
            "url": "仓库URL",
            "api_key": "API密钥",
            "platform": "平台类型",
            "project_id": "项目ID"
        }
    
    Returns:
        JSON响应包含创建的仓库信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取请求参数
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        platform = data.get('platform', 'yunxiao').strip()
        project_id = data.get('project_id', '').strip()
        
        # 验证必填字段
        if not all([name, url, api_key]):
            return validation_error_response("仓库名称、URL和API密钥不能为空")
        
        # 验证URL格式
        if not validate_git_url(url):
            return validation_error_response("仓库URL格式不正确")
        
        # 检查仓库是否已存在
        existing_repo = Repository.query.filter_by(
            user_id=current_user.id,
            url=url
        ).first()
        
        if existing_repo:
            return conflict_response("该仓库已存在")
        
        # 验证API密钥和仓库访问权限
        validation_result = validate_repository_access(url, api_key, platform, project_id)
        if not validation_result['valid']:
            return validation_error_response(validation_result['message'])
        
        # 创建新仓库
        repository = Repository(
            user_id=current_user.id,
            name=name,
            url=url,
            platform=platform,
            project_id=project_id
        )
        
        # 加密存储API密钥
        repository.set_api_key(api_key)
        
        db.session.add(repository)
        db.session.commit()
        
        # 返回仓库信息
        repo_data = repository.to_dict()
        repo_data['stats'] = {
            'commits_count': 0,
            'merge_requests_count': 0
        }
        
        return created_response(
            data=repo_data,
            message="仓库添加成功"
        )
        
    except IntegrityError:
        db.session.rollback()
        return conflict_response("仓库已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加仓库失败: {str(e)}")
        return error_response("添加仓库失败")

@api_bp.route('/<int:repo_id>', methods=['GET'])
@token_required
def get_repository(current_user, repo_id):
    """
    获取仓库详情
    
    Headers:
        Authorization: Bearer <access_token>
    
    Path Parameters:
        repo_id (int): 仓库ID
    
    Returns:
        JSON响应包含仓库详细信息
    """
    try:
        # current_user已通过装饰器传入
        
        # 查找仓库
        repository = Repository.query.filter_by(user_id=current_user.id, id=repo_id).first()
        if not repository:
            return not_found_response("仓库不存在")
        
        # 获取仓库详细信息
        repo_data = repository.to_dict()
        repo_data['stats'] = {
            'commits_count': repository.get_commit_count(),
            'merge_requests_count': repository.get_merge_request_count(),
            'last_sync_at': repository.last_sync_at.isoformat() + 'Z' if repository.last_sync_at else None
        }
        
        return success_response(
            data=repo_data,
            message="获取仓库详情成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取仓库详情失败: {str(e)}")
        return error_response("获取仓库详情失败")

@api_bp.route('/<int:repo_id>', methods=['PUT'])
@token_required
def update_repository(current_user, repo_id):
    """
    更新仓库信息
    
    Headers:
        Authorization: Bearer <access_token>
    
    Path Parameters:
        repo_id (int): 仓库ID
    
    Request Body:
        {
            "name": "新仓库名称",
            "api_key": "新API密钥",
            "is_active": true
        }
    
    Returns:
        JSON响应包含更新后的仓库信息
    """
    try:
        # current_user已通过装饰器传入
        
        # 查找仓库
        repository = Repository.query.filter_by(user_id=current_user.id, id=repo_id).first()
        if not repository:
            return not_found_response("仓库不存在")
        
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取更新字段
        name = data.get('name', '').strip()
        api_key = data.get('api_key', '').strip()
        is_active = data.get('is_active')
        
        # 更新仓库信息
        update_data = {}
        
        if name and name != repository.name:
            update_data['name'] = name
        
        if api_key:
            # 验证新的API密钥
            validation_result = validate_repository_access(
                repository.url, api_key, repository.platform, repository.project_id
            )
            if not validation_result['valid']:
                return validation_error_response(validation_result['message'])
            
            repository.set_api_key(api_key)
        
        if is_active is not None:
            update_data['is_active'] = bool(is_active)
        
        # 应用更新
        if update_data:
            repository.update_info(**update_data)
        
        db.session.commit()
        
        # 返回更新后的仓库信息
        repo_data = repository.to_dict()
        repo_data['stats'] = {
            'commits_count': repository.get_commits_count(),
            'merge_requests_count': repository.get_merge_requests_count()
        }
        
        return updated_response(
            data=repo_data,
            message="仓库更新成功"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新仓库失败: {str(e)}")
        return error_response("更新仓库失败")

@api_bp.route('/<int:repo_id>', methods=['DELETE'])
@token_required
def delete_repository(current_user, repo_id):
    """
    删除仓库
    
    Headers:
        Authorization: Bearer <access_token>
    
    Path Parameters:
        repo_id (int): 仓库ID
    
    Returns:
        JSON响应确认删除成功
    """
    try:
        # current_user已通过装饰器传入
        
        # 查找仓库
        repository = Repository.query.filter_by(user_id=current_user.id, id=repo_id).first()
        if not repository:
            return not_found_response("仓库不存在")
        
        # 删除相关数据
        # 删除提交记录
        Commit.query.filter_by(repository_id=repo_id).delete()
        
        # 删除合并请求
        MergeRequest.query.filter_by(repository_id=repo_id).delete()
        
        # 删除仓库
        db.session.delete(repository)
        db.session.commit()
        
        return deleted_response("仓库删除成功")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除仓库失败: {str(e)}")
        return error_response("删除仓库失败")

@api_bp.route('/<int:repo_id>/sync', methods=['POST'])
@token_required
def sync_repository(current_user, repo_id):
    """
    同步仓库数据
    
    Headers:
        Authorization: Bearer <access_token>
    
    Path Parameters:
        repo_id (int): 仓库ID
    
    Request Body:
        {
            "force": false,
            "sync_commits": true,
            "sync_merge_requests": true
        }
    
    Returns:
        JSON响应包含同步结果
    """
    try:
        # current_user已通过装饰器传入
        
        # 查找仓库
        repository = Repository.query.filter_by(user_id=current_user.id, id=repo_id).first()
        if not repository:
            return not_found_response("仓库不存在")
        
        if not repository.is_active:
            return validation_error_response("仓库已被禁用")
        
        data = request.get_json() or {}
        force = data.get('force', False)
        sync_commits = data.get('sync_commits', True)
        sync_merge_requests = data.get('sync_merge_requests', True)
        
        # 更新同步状态
        repository.update_sync_status('syncing')
        db.session.commit()
        
        sync_result = {
            'commits_synced': 0,
            'merge_requests_synced': 0,
            'errors': []
        }
        
        try:
            # 同步提交记录
            if sync_commits:
                commits_result = sync_repository_commits(repository, force)
                sync_result['commits_synced'] = commits_result['synced_count']
                if commits_result['errors']:
                    sync_result['errors'].extend(commits_result['errors'])
            
            # 同步合并请求
            if sync_merge_requests:
                mrs_result = sync_repository_merge_requests(repository, force)
                sync_result['merge_requests_synced'] = mrs_result['synced_count']
                if mrs_result['errors']:
                    sync_result['errors'].extend(mrs_result['errors'])
            
            # 更新同步状态和时间
            repository.update_sync_status('completed')
            repository.last_sync_at = datetime.utcnow()
            db.session.commit()
            
            return success_response(
                data=sync_result,
                message="仓库同步完成"
            )
            
        except Exception as sync_error:
            # 同步失败，更新状态
            repository.update_sync_status('failed')
            db.session.commit()
            
            sync_result['errors'].append(str(sync_error))
            return error_response(
                message="仓库同步失败",
                details=sync_result
            )
        
    except Exception as e:
        current_app.logger.error(f"同步仓库失败: {str(e)}")
        return error_response("同步仓库失败")

@api_bp.route('/platforms', methods=['GET'])
@token_required
def get_supported_platforms(current_user):
    """
    获取支持的平台列表
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        JSON响应包含支持的平台信息
    """
    try:
        platforms = [
            {
                'id': 'yunxiao',
                'name': '阿里云效',
                'description': '阿里云效代码管理平台',
                'api_docs': 'https://help.aliyun.com/zh/yunxiao/developer-reference/api-reference-standard-proprietary/',
                'required_fields': ['api_key', 'project_id']
            }
            # 可以在这里添加更多平台支持
        ]
        
        return success_response(
            data=platforms,
            message="获取支持平台成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取支持平台失败: {str(e)}")
        return error_response("获取支持平台失败")

@api_bp.route('/validate', methods=['POST'])
@token_required
def validate_repository(current_user):
    """
    验证仓库访问权限
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "url": "仓库URL",
            "api_key": "API密钥",
            "platform": "平台类型",
            "project_id": "项目ID"
        }
    
    Returns:
        JSON响应包含验证结果
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        platform = data.get('platform', 'yunxiao').strip()
        project_id = data.get('project_id', '').strip()
        
        if not all([url, api_key]):
            return validation_error_response("仓库URL和API密钥不能为空")
        
        # 验证仓库访问权限
        validation_result = validate_repository_access(url, api_key, platform, project_id)
        
        if validation_result['valid']:
            return success_response(
                data=validation_result['data'],
                message="仓库验证成功"
            )
        else:
            return validation_error_response(validation_result['message'])
        
    except Exception as e:
        current_app.logger.error(f"验证仓库失败: {str(e)}")
        return error_response("验证仓库失败")

def validate_repository_access(url, api_key, platform, project_id):
    """
    验证仓库访问权限
    
    Args:
        url (str): 仓库URL
        api_key (str): API密钥
        platform (str): 平台类型
        project_id (str): 项目ID
    
    Returns:
        dict: 验证结果
    """
    try:
        if platform == 'yunxiao':
            return validate_yunxiao_repository(url, api_key, project_id)
        else:
            return {
                'valid': False,
                'message': f'不支持的平台: {platform}'
            }
    except Exception as e:
        current_app.logger.error(f"验证仓库访问权限失败: {str(e)}")
        return {
            'valid': False,
            'message': '验证仓库访问权限时发生错误'
        }

def validate_yunxiao_repository(url, api_key, project_id):
    """
    验证阿里云效仓库访问权限
    
    Args:
        url (str): 仓库URL
        api_key (str): API密钥
        project_id (str): 项目ID
    
    Returns:
        dict: 验证结果
    """
    try:
        # 这里应该调用阿里云效API来验证访问权限
        # 由于这是一个示例，我们简化处理
        
        # 基本URL格式验证
        if 'codeup.aliyun.com' not in url and 'yunxiao.aliyun.com' not in url:
            return {
                'valid': False,
                'message': '不是有效的阿里云效仓库URL'
            }
        
        # API密钥格式验证
        if len(api_key) < 10:
            return {
                'valid': False,
                'message': 'API密钥格式不正确'
            }
        
        # 在实际应用中，这里应该调用云效API验证权限
        # 例如：获取项目信息、仓库信息等
        
        return {
            'valid': True,
            'message': '验证成功',
            'data': {
                'platform': 'yunxiao',
                'project_id': project_id,
                'repository_name': url.split('/')[-1].replace('.git', '')
            }
        }
        
    except Exception as e:
        current_app.logger.error(f"验证阿里云效仓库失败: {str(e)}")
        return {
            'valid': False,
            'message': '验证仓库访问权限时发生错误'
        }

def sync_repository_commits(repository, force=False):
    """
    同步仓库提交记录
    
    Args:
        repository (Repository): 仓库对象
        force (bool): 是否强制同步
    
    Returns:
        dict: 同步结果
    """
    try:
        # 这里应该调用相应平台的API获取提交记录
        # 由于这是一个示例，我们返回模拟结果
        
        return {
            'synced_count': 0,
            'errors': []
        }
        
    except Exception as e:
        current_app.logger.error(f"同步提交记录失败: {str(e)}")
        return {
            'synced_count': 0,
            'errors': [str(e)]
        }

def sync_repository_merge_requests(repository, force=False):
    """
    同步仓库合并请求
    
    Args:
        repository (Repository): 仓库对象
        force (bool): 是否强制同步
    
    Returns:
        dict: 同步结果
    """
    try:
        # 这里应该调用相应平台的API获取合并请求
        # 由于这是一个示例，我们返回模拟结果
        
        return {
            'synced_count': 0,
            'errors': []
        }
        
    except Exception as e:
        current_app.logger.error(f"同步合并请求失败: {str(e)}")
        return {
            'synced_count': 0,
            'errors': [str(e)]
        }



@api_bp.route('/yunxiao/search', methods=['GET'])
@token_required
def search_yunxiao_repositories(current_user):
    """
    按仓库名称查询云效仓库列表
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        page (int): 页码，默认1
        per_page (int): 每页数量，默认50，最大100
        search (str): 搜索关键词，必填，用于模糊匹配仓库路径
    
    Returns:
        JSON响应包含云效仓库列表
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)  # 默认50，最大100
        search = request.args.get('search', '').strip()
        
        # 验证搜索关键词是否提供
        if not search:
            current_app.logger.error("搜索关键词为空")
            return validation_error_response("请输入仓库名称进行搜索")
        
        # 检查云效API配置
        api_base_url = current_app.config.get('ALIYUNXIAO_API_BASE_URL')
        access_token = current_app.config.get('ALIYUNXIAO_ACCESS_TOKEN')
        organization_id = current_app.config.get('ALIYUNXIAO_ORGANIZATION_ID')
        
        current_app.logger.info(f"云效API配置 - URL: {api_base_url}, Token: {'已设置' if access_token else '未设置'}, OrgID: {organization_id}")
        
        if not all([api_base_url, access_token, organization_id]):
            current_app.logger.error(f"云效API配置不完整 - URL: {api_base_url}, Token: {'已设置' if access_token else '未设置'}, OrgID: {organization_id}")
            return error_response("云效API配置不完整，请联系管理员")
        
        # 构建API请求URL（使用正确的云效API路径）
        url = f"{api_base_url}/oapi/v1/codeup/organizations/{organization_id}/repositories"
        headers = {
            'x-yunxiao-token': access_token,
            'Content-Type': 'application/json'
        }
        
        # 构建查询参数（使用云效API的参数格式）
        params = {
            'page': page,
            'perPage': per_page,  # 云效API使用perPage而不是per_page
            'orderBy': 'created_at',
            'sort': 'desc',
            'archived': 'false'
        }
        if search:
            params['search'] = search
        
        # 记录请求详情
        current_app.logger.info(f"云效API请求URL: {url}")
        current_app.logger.info(f"云效API请求头: {headers}")
        current_app.logger.info(f"云效API请求参数: {params}")
        
        # 调用云效API
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        current_app.logger.info(f"云效API响应状态码: {response.status_code}")
        current_app.logger.info(f"云效API响应内容: {response.text}")  # 记录完整响应内容
        
        if response.status_code == 200:
            try:
                # 云效API直接返回仓库数组，不是包含result字段的对象
                repositories = response.json()
                if not isinstance(repositories, list):
                    current_app.logger.error(f"云效API响应格式错误，期望数组但得到: {type(repositories)}")
                    return error_response("云效API响应格式错误")
            except json.JSONDecodeError as e:
                current_app.logger.error(f"云效API响应JSON解析失败: {str(e)}")
                current_app.logger.error(f"响应内容: {response.text}")
                return error_response("云效API响应格式错误")
            
            # 获取用户已有的仓库列表，用于标记状态
            existing_repos = Repository.query.filter_by(user_id=current_user.id).all()
            existing_urls = {repo.url for repo in existing_repos}
            existing_tracked = {repo.url: repo.is_tracked for repo in existing_repos}
            
            # 处理仓库数据，添加状态信息
            processed_repos = []
            for repo in repositories:
                clone_url = repo.get('cloneUrl', {}).get('https', '')
                processed_repo = {
                    'id': repo.get('id'),
                    'name': repo.get('name', ''),
                    'full_name': repo.get('nameWithNamespace', ''),
                    'description': repo.get('description', ''),
                    'url': repo.get('webUrl', ''),
                    'clone_url': clone_url,
                    'visibility': 'private' if repo.get('visibility') == 0 else 'public',
                    'created_at': repo.get('createdAt', ''),
                    'last_activity': repo.get('lastActivityAt', ''),
                    'is_added': clone_url in existing_urls,
                    'is_tracked': existing_tracked.get(clone_url, False)
                }
                processed_repos.append(processed_repo)
            
            # 云效API分页机制：如果返回的数据少于请求的per_page，说明已到最后一页
            # 由于云效API不直接返回总数，我们需要估算总数
            has_more = len(repositories) == per_page
            estimated_total = (page - 1) * per_page + len(repositories)
            if has_more:
                # 如果还有更多数据，总数至少是当前估算值+1
                estimated_total += 1
            
            return paginated_response(
                items=processed_repos,
                page=page,
                per_page=per_page,
                total=estimated_total,
                message="获取云效仓库列表成功"
            )
        else:
            current_app.logger.error(f"云效API请求失败: {response.status_code} - {response.text}")
            return error_response("获取仓库列表失败，请重试")
            
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"云效API请求异常: {str(e)}")
        return error_response("网络请求失败，请检查网络连接")
    except json.JSONDecodeError as e:
        current_app.logger.error(f"云效API请求异常: {str(e)}")
        return error_response("云效API响应格式错误")
    except Exception as e:
        current_app.logger.error(f"获取云效仓库列表失败: {str(e)}")
        return error_response("获取仓库列表失败，请重试")


@api_bp.route('/<int:repo_id>/track', methods=['POST'])
@token_required
def add_to_tracking(current_user, repo_id):
    """
    将仓库加入统计
    
    Args:
        repo_id: 仓库ID
    
    Returns:
        JSON响应，包含操作结果
    """
    try:
        # 查找仓库
        repository = Repository.query.filter_by(
            id=repo_id,
            user_id=current_user.id
        ).first()
        
        if not repository:
            return not_found_response("仓库不存在")
        
        # 检查是否已经在统计中
        if repository.is_tracked:
            return conflict_response("该仓库已经在统计中")
        
        # 加入统计
        repository.is_tracked = True
        db.session.commit()
        
        return success_response(
            data=repository.to_dict(),
            message="仓库已成功加入统计"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"加入统计失败: {str(e)}")
        return error_response("加入统计失败，请重试")


@api_bp.route('/<int:repo_id>/untrack', methods=['POST'])
@token_required
def remove_from_tracking(current_user, repo_id):
    """
    将仓库移出统计
    
    Args:
        repo_id: 仓库ID
    
    Returns:
        JSON响应，包含操作结果
    """
    try:
        # 查找仓库
        repository = Repository.query.filter_by(
            id=repo_id,
            user_id=current_user.id
        ).first()
        
        if not repository:
            return not_found_response("仓库不存在")
        
        # 检查是否在统计中
        if not repository.is_tracked:
            return conflict_response("该仓库未在统计中")
        
        # 移出统计
        repository.is_tracked = False
        db.session.commit()
        
        return success_response(
            data=repository.to_dict(),
            message="仓库已成功移出统计"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"移出统计失败: {str(e)}")
        return error_response("移出统计失败，请重试")


@api_bp.route('/yunxiao/add', methods=['POST'])
@token_required
def add_yunxiao_repository(current_user):
    """
    从云效仓库列表中添加仓库到用户的仓库管理中
    
    Request Body:
        {
            "repository_id": "仓库ID",
            "name": "仓库名称",
            "clone_url": "克隆地址",
            "web_url": "网页地址",
            "description": "仓库描述"
        }
    
    Returns:
        JSON响应，包含添加的仓库信息
    """
    try:
        data = request.get_json()
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 验证必需字段
        required_fields = ['repository_id', 'name', 'clone_url']
        current_app.logger.info(f"接收到的数据: {data}")
        for field in required_fields:
            field_value = data.get(field)
            current_app.logger.info(f"字段 {field} 的值: {field_value}")
            if not field_value:
                current_app.logger.error(f"字段验证失败: {field} 为空或不存在")
                return validation_error_response(f"缺少必需字段: {field}")
        
        # 检查仓库是否已存在
        existing_repo = Repository.query.filter_by(
            user_id=current_user.id,
            url=data['clone_url']
        ).first()
        
        if existing_repo:
            return conflict_response("该仓库已存在")
        
        # 获取云效API配置
        access_token = current_app.config.get('ALIYUNXIAO_ACCESS_TOKEN', '')
        
        # 创建新仓库记录
        repository = Repository(
            user_id=current_user.id,
            name=data['name'],
            url=data['clone_url'],
            api_key=access_token,  # 直接传递api_key参数
            platform='yunxiao',
            project_id=str(data['repository_id']),
            is_tracked=False  # 默认不加入统计
        )
        
        db.session.add(repository)
        db.session.commit()
        
        return created_response(
            data=repository.to_dict(),
            message="仓库添加成功"
        )
        
    except IntegrityError:
        db.session.rollback()
        return conflict_response("仓库已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加云效仓库失败: {str(e)}")
        return error_response("添加仓库失败，请重试")