"""Download the 12 voice-over clips and stitch them into one MP3, in order.
Run anywhere:   python3 stitch-npr-audio.py
Output:         the-letter-that-refused-to-send.mp3
Uses ffmpeg if installed; otherwise falls back to a direct byte concat, which plays fine.
"""
import urllib.request, subprocess, shutil, pathlib, sys

B = "https://cms-toolkit-artifacts.artlist.io/content/-t-e-x-t_-t-o_-s-p-e-e-c-h-v1/"
K = "&Key-Pair-Id=K2ZDLYDZI2R1DF&Signature="
CLIPS = [
 ("media__7/-t-e-x-t_-t-o_-s-p-e-e-c-h-452fd63c-366d-4b57-b39e-07d9006ba893.mp3?Expires=2104402717", "Ztl6HFrtbsNR0p~8EhZk8IQb1xFXQYM7qbHafnhCpdMgTfX9hLk2gcgLrDKi2T3EpSYtly~C10LPPVGSPPGvgQB5py319ibuF-KoNH~c1Z1JRDDXdZTZSmoRhhVLcrh-wZpgkQvXU~u-X5kVaJ~5kfpJXVUH7JCnLgFgQCuB~KvIzZiiSgxRD1FYxTxQuhMDBfidqZ6cIhv0QDND4cU7WHwSFwUE84IDAZ-BcyXPRm1Je4uIb~FI0A-a4Cyr7WaRWzercvfsF~i1fwoaUxMGBeNILV0ToqaX1hYzew4hywZ7LGTSuscKluFenO9Gu8UGAKtJDzFxXKl~-A03gwEODw__"),
 ("media__2/-t-e-x-t_-t-o_-s-p-e-e-c-h-57c9a48e-0ae1-4a67-a48e-ef3d0b738110.mp3?Expires=2104402717", "KzPJs86pwCFywpVbUoznARIr3ss~RoQg8UezUZMWPCpmPnCmpbQLju1~jHjUzPQMWmWpxboc19fUEV-tHj0oyz2RIwXw2mhqX~N7ZsFx9h95rNpGGcdZ2oLhwDMYDnu5LlYj4wwd0RilUbh29lCVCfBZvPJXp0VdgSgAT1jQtHSFZTvwNJFEOB94bbRmHgAb8qVueh8FCDh0AhB35jJie4dx-JnptnBfFjR6NibsBAiJjpdkRr2~rsKl-D4ZtRNF37ZXjmDCkDkfefsTxaN8I7Yc0RVa89lbfyQaumHc~ZHinYAtkeZ6-P0wM-JReSEk5c5aJSD5AAivqnR9HOUpAg__"),
 ("media__9/-t-e-x-t_-t-o_-s-p-e-e-c-h-73a31dde-ad9f-46c4-9a12-3fab511177a0.mp3?Expires=2104402717", "1GOaQZKIcNn4UjbYGj-qdT1cUFbONO3~vSi6jf-lrDlRyP5CC9jwb7PuyC0jXKqlFQEvNsv3fWzZMXMx2MLQ4qAA28sFv0rInPnc2ReQjqgO1Ff827gHRYGdwZB39lgTGb~p44ZBX6~etIt0qX72aspjk212K0voobCiPF7kd7oX4OPew944TpilPIY-itPhqs4nxHpOq2v2gOS37B9lBDJrLjalvh3iZ-tYxgLPsaj1cAreWKd-kX-fisLEo2OnAhdEiIm0xti-LAayTyAg62YvFGPGg1QlEJXIpPY4jmCsLweSsP6d3G~x6TYGREgYlUCpuWIIUH4RE~UhWU2b2A__"),
 ("media__8/-t-e-x-t_-t-o_-s-p-e-e-c-h-c24b488d-dc1b-435a-b965-2fef2aed16b9.mp3?Expires=2104402717", "dMrcfBBZkij0MRROOld1f1J97A50LmP1VI~N4A6kclCcKCk2r-q2rLHnaOfMFs2DG14x5woQ5qIeqihJUSllCsp~MVGvXX6pdrCOVy9HwJ9FkiXARwRtoFJ65PYX97jcV2uosiGArBvdneRTanWwtUSCnFSXCDGnepRDy~BzoBTnPJgljKn8e~JfiSPN7TZ4cYPVXduh50t1PF4UBjG6GvhVVVWZweJyHDR0K8UlfslqTewB8cf~qRJ4tQapy9JZgGEuMjgSar4pwM054RUwncHKE5cgwcThUvV7n2bPjNIHuhGnd9BiLNnYNfJ2ejEWRnBrVducFMry9hUEI~aS6g__"),
 ("media__3/-t-e-x-t_-t-o_-s-p-e-e-c-h-a457079e-d2fe-4a5f-9f12-31a86dc093c3.mp3?Expires=2104402717", "LPAw-JTRobWcUKHKq6LKtUGSLlEqJSs7-dFmVs1-7IUNesZJ4zl7MP~8lOKhVI8kpKx7vuptPGbxvq7-otdkVBiUiAAmCnUprQy52rgGUYB8B4rY7ODJk1XA6FM2G5x2xT8Kh9cS2o6ne07ZbTpbmcC-a3tMF-q9-M0OxjlcasaSFzGLsZDiWit4g3pxQSUVDdfVnfAqn~suCBvesPABM~x1EevN6sRwE62NnCPYjPtocEujkDOjtnT2hXFxkBsqmaREv0tnL7fiA7gMP3vNsLW4c6hWWygzm9NPxyUgINKJyBFxvPLq52-jnsgTSzmjHmgiTTh6A4i6byEuRYrHrQ__"),
 ("media__6/-t-e-x-t_-t-o_-s-p-e-e-c-h-75af5ec8-96b3-4843-804d-229bce90333a.mp3?Expires=2104402717", "aw7QdCqFnYhktZ7O5oS~90wFnE7G6ZofmdRCOE6e85UonKgfRDw61SoPhrk8mYDmUauSO2NLEzS6Joz04JFguxIcjpCwdUftH8yUeVAiOJqd99sZ7EUrEmcJNCStTVpGDVFZDR5xN2Ie4Urmh5C0pkdpaHheZkLdOQzwGd1CHnwJPqJQJlMC4xORjJSf6Vxv95~Ht7siiLKTHdWSydYdtHgZUnQbrkxMYPPHDTVhj9nL4US93E8chYxrKd0Rkn7HHcG7s8j3vD-VLb8KVgmFv0U5xpplSDzGA7I8MmCjN6p0SBELfBcKvOqDZ8jZdGo4CsN21hSraW1P4REr~fT~1g__"),
 ("media__10/-t-e-x-t_-t-o_-s-p-e-e-c-h-6433e52b-a4ba-4dce-b603-21fe20ea250b.mp3?Expires=2104402717", "0LYSQIH3RgHQE9uayg4-iGTXeI2BYOEvthDe9AwttD07LkQxvRTpi5fIyMaSAvcFVD5~AOKUaqnPfvYCmYa6MtBvFvrlW6G48GKwma6JJHjZkgPhP0zResX5gmfsDzJgaMGBOb-Vl3h6EgLm7DnDi8Vez~3Mj4rkPJtkwWlIYhiZodf7fPmO21GhmOICFO6cc7odhR21I5X9ozjJeHVs0-7o6Q8JzmTOeRkdC0WLN9K1O54VUmCSGGe-HJm1DvWAFaXyp-hAjtFY62fbtMauzQWChlnS3yz5IgW7bMTe3b7K9ZWGZXxEV2PBcqX9tYS~G339v0g590SDxEPOT2zP2A__"),
 ("media__10/-t-e-x-t_-t-o_-s-p-e-e-c-h-c3703166-cc8b-44eb-8351-a2d6a4065505.mp3?Expires=2104402717", "mawuHvVdCYzfO2K7fd6bEI6em~r12lTDLYYgo-TB5vdkBK6NQbmPwJewtDeU0jC6cvVptWauzcqvqFbmMdPjrvGi-G7CsqCCkxZVjT0oHjSz4Ekj-kkA6CwsOHIqwfLwCFuLaN9psg6OTjB76xiPGJ5pH2--3X3fbNzeTCVds5kSjhd0jk2m-eH~h3GLZHyZ9JtN5052U1sZuqjcfKG5CArntjXeEAWyfISxMSPJUM383E4wFnWPyIzQyaYworEIUYL4zFPS~Q7tcI09WRrsMW1aZPRz11-~fFDYX33ucTpSzCVYcxaX7tk2qT~mAM110KZ2fU2FAcxMXCBkWC8yvg__"),
 ("media__2/-t-e-x-t_-t-o_-s-p-e-e-c-h-51c24222-2741-4b57-a290-abc380783cfa.mp3?Expires=2104402717", "irLydKgsfjwDaejltBhcGB0K5TZCRzzU9bhGNmee-5Cff1x-RkrDuuRzC44~ur3hGjD~5XtFesSgOfAKCOm4BkJ54Pk6~ybbPbyt7YxLcXrRnWJ92S1LbnXrB4BhZksRvXqm4~VoLGQzQhzq2PMcC5rbUCSzVshcoLPzaqofPd54bIMY9xrBC1hVJU84MykiHdzIqsA7n-CQp0-YbXR2VNWkrokBYzqtrz22Spq7gmjAbvi4SJl~cp3z~PFS1ecw0m0yRBCshGzWlQnqzWorXUwFgOmc0Y4zQWUZZohCSxAfODC1HvaTx~KrJQQlX7mjecKl8zhfQW9auoFvePDOuw__"),
 ("media__7/-t-e-x-t_-t-o_-s-p-e-e-c-h-f8ea9f7b-87e5-4641-8749-ad62753bf7c0.mp3?Expires=2104402723", "Zh~MjrMM4iU79Hi6TVMvF4fDT0yrHieku43C55EyBbkGzC9bBPxM26Y~uqFHtJue7HiBXh-mChCr1RQfqfeX8i6LbPAUYvTxeEUjVx4lYnxpq~kgdFCMUoyvplCC6ryFa-EjWVa4jrHkYzAM2ZUW1KsU1Ug8tSu3SSQbLUXsql55Q0zxhUSoaA2PQ1efRQgNnPAVKVnvew8MMwbOd0RHibcuSSaUM52Uy0KUz~lBvCJbKUIi57q9pRq7eMngPk-IRqCtZLbcvC6-8xvoEh5mRsRCxFabI9c6AM9THwRJtwJOgJAFVLDfhSDpx0vJJeaWfV0wPj48evUupb5ucED6fw__"),
 ("media__4/-t-e-x-t_-t-o_-s-p-e-e-c-h-d17edb1e-4869-4295-9b67-c75842e9bbcc.mp3?Expires=2104402723", "1YbJndsjcpIwr1JITqUKW9YYxHs5GqSJ5Fh350ZQqpEX-MZg6PXcQrqBjaQX9nJc~krzuj3a308zcJ7f5tho9nunxitVyF-IJD14eIdt36sGolCT6sFXiqXN~teOvQE0VtLuvsJtXbRrrqcwI5RQe52jevFrE36IZv0H0h6UgsIxZgiofxSP7HgigoZ1mOX7ppiFsWb3oSsCNpq1-MH-xgabBBkWBPhezN0eRxuAviPxXyPv1b6mMLEGoh3x8W2xacY5--GLDhgkXRiptR1jycLGtg1OBptjfOaybJGdJWcVCf-xN-CHjC9fwLEL5KFOgmmsy0bE3UQxrv5CJshZww__"),
 ("media__6/-t-e-x-t_-t-o_-s-p-e-e-c-h-947f7efd-98f6-4421-af33-6ec9dfd547cb.mp3?Expires=2104402723", "wlgO~PIuBT4apg9bspFVGzEkj6cogJWNEEHVfLbbTepKv6HpH5AxfirsTm1OBsvzi~xl~l82H1b2Tjve9PtNFsGVVyoq7l1d9vus2Ab6bArDMvtO3b5jF0Fc2ps~OF4wyzfbQOj34G9Sg9KX-k7ev6Kg3-GyESQyzp9VLLywyTYRj-gQjKxfSa2Rua9oY9cC9IWJZss1QG9UlJvKoG2mTsu0cTPAfiRerHIQqBwQHwnOIveW4cuJ0zO9UowW4YCmeJOVITrQGQMgO52zT94yIM-5OKuB1g8pfuJK~jzJ-3r396hVjh7CPtKHUTp3ZqUpzaXsFSMypwcur7R371YWQA__"),
]

out = pathlib.Path("the-letter-that-refused-to-send.mp3")
work = pathlib.Path("npr_clips"); work.mkdir(exist_ok=True)
paths = []
for i, (path, sig) in enumerate(CLIPS, 1):
    f = work / f"{i:02d}.mp3"
    if not f.exists():
        print(f"downloading clip {i}/12 ...", end=" ", flush=True)
        urllib.request.urlretrieve(B + path + K + sig, f)
        print(f"{f.stat().st_size//1024} KB")
    paths.append(f)

if shutil.which("ffmpeg"):
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in paths))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(out)], check=True)
    print("stitched with ffmpeg")
else:
    with out.open("wb") as o:
        for p in paths: o.write(p.read_bytes())
    print("stitched by direct concat (ffmpeg not found - plays fine, install ffmpeg for cleaner joins)")

print(f"\nDone: {out}  ({out.stat().st_size//1024} KB)")
print("Clips kept in npr_clips/ in case you want to re-edit. Order: 1 Dana cold open ... 12 Ray close.")
