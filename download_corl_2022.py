'''Downloads the metadata, paper PDFs, and the supplementary materials from OpenReview.'''

import argparse
import json
import os
from collections import defaultdict
from tqdm import tqdm
import openreview


# Needs to be modified based on the conference
CONFERENCE_NAME = 'corl22'
CONFERENCE_INVITATION = 'robot-learning.org/CoRL/2022/Conference/-/Blind_Submission'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--outdir', default='./', help='directory where data should be saved')
    parser.add_argument(
        '--get_pdfs', default=False, action='store_true', help='if included, download pdfs')
    parser.add_argument(
        '--get_supplementary', default=False, action='store_true', help='if included, download supplementary material')
    parser.add_argument('--baseurl', default='https://api.openreview.net')
    parser.add_argument('--username', default='', help='defaults to empty string (guest user)')
    parser.add_argument('--password', default='', help='defaults to empty string (guest user)')

    args = parser.parse_args()
    outdir = args.outdir

    # Initiates the OpenReview client.
    client = openreview.Client(
        baseurl=args.baseurl,
        username=args.username,
        password=args.password)

    # Retrieves the meta data.
    submissions = openreview.tools.iterget_notes(
        client, invitation=CONFERENCE_INVITATION)
    submissions_by_forum = {n.forum: n for n in submissions}
    metadata = []
    for forum in submissions_by_forum:
        submission_content = submissions_by_forum[forum].content
        forum_metadata = {
            'forum': forum,
            'submission_content': submission_content
        }
        metadata.append(forum_metadata)

    outdir = os.path.join(outdir, CONFERENCE_NAME)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print('writing metadata to file...')
    # write the metadata, one JSON per line:
    with open(os.path.join(outdir, CONFERENCE_NAME + '__metadata.jsonl'), 'w') as file_handle:
        for forum_metadata in metadata:
            file_handle.write(json.dumps(forum_metadata) + '\n')


    # Downloads the paper PDFs.
    if args.get_pdfs:
        for forum_metadata in tqdm(metadata, desc='getting pdfs'):
            pdf_binary = client.get_pdf(forum_metadata['forum'])
            pdf_outfile = os.path.join(outdir, '{}.pdf'.format(forum_metadata['forum']))
            print("downloading {}".format(pdf_outfile))
            with open(pdf_outfile, 'wb') as file_handle:
                file_handle.write(pdf_binary)

    # Downloads the supplementary materials.
    if args.get_supplementary:
        for forum_metadata in tqdm(metadata, desc='getting supplementary materials'):
            try:
                supplementary_binary = client.get_attachment(forum_metadata['forum'], 'supplementary_material')
                supplementary_outfile = os.path.join(outdir, '{}_supp.zip'.format(forum_metadata['forum']))
                print("downloading {}".format(supplementary_outfile))
                with open(supplementary_outfile, 'wb') as file_handle:
                    file_handle.write(supplementary_binary)
            except openreview.OpenReviewException:
                print("{} not found".format(supplementary_outfile))
